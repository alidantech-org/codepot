from __future__ import annotations

import base64
import threading
from collections.abc import Iterator, Mapping
from dataclasses import dataclass

from dryv.features.artifacts import (
    ManagedOutput,
    ManagedOutputManifest,
    ProjectPathState,
    ProjectSnapshot,
)
from dryv.features.authoring import AuthorRequest, AuthorSource
from dryv.features.cache import CacheMode
from dryv.features.packs import PackTemplateResource
from dryv.features.planning import PlanningCandidate, TraceFact
from dryv.features.scheduling import CancellationToken
from dryv.runtime import (
    AuthorSourceBuild,
    AvailableRenderSession,
    BuildPack,
    BuildRequest,
    BuildResource,
    BuildResult,
    DryvRuntime,
)

API_VERSION = "dryv.api/v1"


class ApiContractError(ValueError):
    def __init__(self, code: str, message: str, *, path: str = "$") -> None:
        super().__init__(f"{path}: {message}")
        self.code = code
        self.message = message
        self.path = path


@dataclass(frozen=True, slots=True)
class RegisteredAuthorSession:
    connection_id: str
    session: object


@dataclass(frozen=True, slots=True)
class RegisteredRenderSession:
    connection_id: str
    session: object


class SessionRegistry:
    """Outer-host connection inventory; Dryv Engine never discovers connections itself."""

    def __init__(self) -> None:
        self._authors: dict[str, object] = {}
        self._renderers: dict[str, object] = {}
        self._lock = threading.Lock()

    def register_author(self, connection_id: str, session: object) -> None:
        _connection_id(connection_id)
        with self._lock:
            if connection_id in self._authors:
                raise ApiContractError(
                    "API_DUPLICATE_AUTHOR_CONNECTION",
                    f"author connection {connection_id!r} is already registered",
                )
            self._authors[connection_id] = session

    def register_renderer(self, connection_id: str, session: object) -> None:
        _connection_id(connection_id)
        with self._lock:
            if connection_id in self._renderers:
                raise ApiContractError(
                    "API_DUPLICATE_RENDER_CONNECTION",
                    f"render connection {connection_id!r} is already registered",
                )
            self._renderers[connection_id] = session

    def author(self, connection_id: str) -> object:
        with self._lock:
            session = self._authors.get(connection_id)
        if session is None:
            raise ApiContractError(
                "API_AUTHOR_CONNECTION_MISSING",
                f"author connection {connection_id!r} is not registered",
            )
        return session

    def renderers(self, connection_ids: tuple[str, ...] | None = None) -> tuple[RegisteredRenderSession, ...]:
        with self._lock:
            if connection_ids is None:
                items = tuple(sorted(self._renderers.items()))
            else:
                missing = tuple(item for item in connection_ids if item not in self._renderers)
                if missing:
                    raise ApiContractError(
                        "API_RENDER_CONNECTION_MISSING",
                        f"render connection {missing[0]!r} is not registered",
                    )
                items = tuple((item, self._renderers[item]) for item in sorted(set(connection_ids)))
        return tuple(RegisteredRenderSession(identity, session) for identity, session in items)


class DryvApiService:
    """Transport-neutral API host around one reusable DryvRuntime instance."""

    def __init__(
        self,
        runtime: DryvRuntime | None = None,
        sessions: SessionRegistry | None = None,
    ) -> None:
        self.runtime = runtime or DryvRuntime()
        self.sessions = sessions or SessionRegistry()
        self._cancellations: dict[str, CancellationToken] = {}
        self._lock = threading.Lock()

    def build(self, document: Mapping[str, object]) -> BuildResult:
        build_id = _string(document.get("buildId"), "$.buildId")
        token = CancellationToken()
        with self._lock:
            if build_id in self._cancellations:
                raise ApiContractError(
                    "API_BUILD_ACTIVE",
                    f"build {build_id!r} is already active",
                    path="$.buildId",
                )
            self._cancellations[build_id] = token
        try:
            request = self._decode_build(document, token)
            return self.runtime.build(request)
        finally:
            with self._lock:
                self._cancellations.pop(build_id, None)

    def build_events(
        self,
        document: Mapping[str, object],
        *,
        artifact_chunk_bytes: int = 64 * 1024,
    ) -> Iterator[dict[str, object]]:
        if artifact_chunk_bytes < 1:
            raise ValueError("artifact_chunk_bytes must be positive")
        result = self.build(document)
        yield {"type": "build-result", "result": encode_build_result(result)}
        if result.artifacts is not None:
            for artifact in result.artifacts.artifacts:
                for chunk in self.runtime.artifacts.stream_artifact(
                    artifact,
                    chunk_size=artifact_chunk_bytes,
                ):
                    yield {
                        "type": "artifact-content",
                        "artifactId": chunk.artifact_id,
                        "offset": chunk.offset,
                        "contentBase64": base64.b64encode(chunk.content).decode("ascii"),
                        "final": chunk.final,
                    }
        yield {
            "type": "stream-complete",
            "buildId": result.build_id,
            "renderComplete": result.render_complete,
        }

    def cancel(self, build_id: str) -> bool:
        with self._lock:
            token = self._cancellations.get(build_id)
        if token is None:
            return False
        token.cancel()
        return True

    def _decode_build(
        self,
        document: Mapping[str, object],
        cancellation: CancellationToken,
    ) -> BuildRequest:
        root = _object(document, "$")
        _unknown(
            root,
            {
                "apiVersion",
                "buildId",
                "resources",
                "project",
                "packs",
                "planningCandidates",
                "precompiledIrResourceId",
                "author",
                "renderSessionIds",
                "previousManagedOutputs",
                "projectSnapshot",
                "cacheMode",
                "commitCache",
            },
            "$",
        )
        if root.get("apiVersion") != API_VERSION:
            raise ApiContractError(
                "API_VERSION",
                f"apiVersion must be {API_VERSION!r}",
                path="$.apiVersion",
            )
        build_id = _string(root.get("buildId"), "$.buildId")
        resources = tuple(
            _decode_resource(item, f"$.resources[{index}]")
            for index, item in enumerate(_list(root.get("resources", []), "$.resources"))
        )
        packs = tuple(
            _decode_pack(item, f"$.packs[{index}]")
            for index, item in enumerate(_list(root.get("packs", []), "$.packs"))
        )
        candidates = tuple(
            _decode_candidate(item, f"$.planningCandidates[{index}]")
            for index, item in enumerate(
                _list(root.get("planningCandidates", []), "$.planningCandidates")
            )
        )
        previous = _decode_previous(root.get("previousManagedOutputs", []))
        snapshot = _decode_snapshot(root.get("projectSnapshot", []))
        renderer_ids_raw = root.get("renderSessionIds")
        renderer_ids = (
            None
            if renderer_ids_raw is None
            else tuple(
                _string(item, "$.renderSessionIds")
                for item in _list(renderer_ids_raw, "$.renderSessionIds")
            )
        )
        render_sessions = tuple(
            AvailableRenderSession(item.connection_id, item.session)  # type: ignore[arg-type]
            for item in self.sessions.renderers(renderer_ids)
        )
        precompiled = _optional_string(
            root.get("precompiledIrResourceId"),
            "$.precompiledIrResourceId",
        )
        author = None
        if root.get("author") is not None:
            author = self._decode_author(root["author"])
        try:
            cache_mode = CacheMode(str(root.get("cacheMode", CacheMode.USE.value)))
        except ValueError as exc:
            raise ApiContractError(
                "API_CACHE_MODE",
                "cacheMode must be use, refresh, or off",
                path="$.cacheMode",
            ) from exc
        commit_cache = _bool(root.get("commitCache", True), "$.commitCache")
        project_raw = root.get("project")
        project = None if project_raw is None else _object(project_raw, "$.project")
        return BuildRequest(
            build_id=build_id,
            resources=resources,
            planning_candidates=candidates,
            project_document=project,
            packs=packs,
            precompiled_ir_resource_id=precompiled,
            author=author,
            render_sessions=render_sessions,
            previous_managed_outputs=previous,
            project_snapshot=snapshot,
            cache_mode=cache_mode,
            commit_cache=commit_cache,
            cancellation=cancellation,
        )

    def _decode_author(self, value: object) -> AuthorSourceBuild:
        item = _object(value, "$.author")
        _unknown(item, {"connectionId", "request"}, "$.author")
        connection_id = _string(item.get("connectionId"), "$.author.connectionId")
        request_raw = _object(item.get("request"), "$.author.request")
        _unknown(
            request_raw,
            {
                "protocolVersion",
                "jobId",
                "requestedIrVersion",
                "sourceKind",
                "sources",
                "options",
            },
            "$.author.request",
        )
        sources = tuple(
            AuthorSource(
                _string(source.get("resourceId"), f"$.author.request.sources[{index}].resourceId"),
                _optional_string(
                    source.get("mediaType"),
                    f"$.author.request.sources[{index}].mediaType",
                ),
            )
            for index, raw in enumerate(
                _list(request_raw.get("sources", []), "$.author.request.sources")
            )
            for source in (_object(raw, f"$.author.request.sources[{index}]"),)
        )
        options_raw = _object(request_raw.get("options", {}), "$.author.request.options")
        options = tuple((key, options_raw[key]) for key in sorted(options_raw))
        request = AuthorRequest(
            _int(request_raw.get("protocolVersion"), "$.author.request.protocolVersion"),
            _string(request_raw.get("jobId"), "$.author.request.jobId"),
            _string(
                request_raw.get("requestedIrVersion"),
                "$.author.request.requestedIrVersion",
            ),
            _string(request_raw.get("sourceKind"), "$.author.request.sourceKind"),
            sources,
            options,
        )
        return AuthorSourceBuild(request, self.sessions.author(connection_id))  # type: ignore[arg-type]


def encode_build_result(result: BuildResult) -> dict[str, object]:
    artifacts = result.artifacts
    return {
        "apiVersion": API_VERSION,
        "buildId": result.build_id,
        "status": result.status.value,
        "success": result.success,
        "renderComplete": result.render_complete,
        "diagnostics": [
            {"code": item.code, "message": item.message, "subject": item.subject}
            for item in result.diagnostics
        ],
        "trace": [
            {
                "stage": item.stage,
                "subject": item.subject,
                "message": item.message,
                "details": dict(item.details),
            }
            for item in result.trace
        ],
        "cache": {
            "contextHits": result.cache.context_hits,
            "contextMisses": result.cache.context_misses,
            "renderHits": result.cache.render_hits,
            "renderMisses": result.cache.render_misses,
        },
        "artifacts": []
        if artifacts is None
        else [
            {
                "artifactId": item.artifact_id,
                "path": item.path,
                "logicalOutputId": item.logical_output_id,
                "contentHash": item.content_hash,
                "ownershipId": item.ownership_id,
                "size": len(item.content),
                "status": item.status.value,
                "dependencies": list(item.dependencies),
                "provenance": {
                    "semanticIds": list(item.provenance.semantic_ids),
                    "packId": item.provenance.pack_id,
                    "selectionKey": item.provenance.selection_key,
                    "templateResourceId": item.provenance.template_resource_id,
                    "invocationId": item.provenance.invocation_id,
                },
            }
            for item in artifacts.artifacts
        ],
        "writeInstructions": []
        if artifacts is None
        else [
            {
                "kind": item.kind.value,
                "path": item.path,
                "ownershipId": item.ownership_id,
                "artifactId": item.artifact_id,
                "expectedPreviousHash": item.expected_previous_hash,
                "newContentHash": item.new_content_hash,
                "reason": item.reason,
            }
            for item in artifacts.instructions
        ],
        "nextManagedOutputs": []
        if artifacts is None
        else [
            {
                "path": item.path,
                "contentHash": item.content_hash,
                "ownershipId": item.ownership_id,
                "artifactId": item.artifact_id,
            }
            for item in artifacts.next_manifest.outputs
        ],
    }


def _decode_resource(value: object, path: str) -> BuildResource:
    item = _object(value, path)
    _unknown(item, {"resourceId", "mediaType", "contentBase64", "contentHash"}, path)
    try:
        content = base64.b64decode(
            _string(item.get("contentBase64"), f"{path}.contentBase64"),
            validate=True,
        )
    except ValueError as exc:
        raise ApiContractError(
            "API_RESOURCE_BASE64",
            "resource contentBase64 is invalid",
            path=f"{path}.contentBase64",
        ) from exc
    return BuildResource(
        _string(item.get("resourceId"), f"{path}.resourceId"),
        _string(item.get("mediaType"), f"{path}.mediaType"),
        content,
        _optional_string(item.get("contentHash"), f"{path}.contentHash"),
    )


def _decode_pack(value: object, path: str) -> BuildPack:
    item = _object(value, path)
    _unknown(item, {"manifest", "manifestResourceId", "templates"}, path)
    templates = tuple(
        PackTemplateResource(
            _string(template.get("resourceId"), f"{path}.templates[{index}].resourceId"),
            _string(template.get("relativePath"), f"{path}.templates[{index}].relativePath"),
            _string(template.get("mediaType"), f"{path}.templates[{index}].mediaType"),
            _string(
                template.get("rendererCapability"),
                f"{path}.templates[{index}].rendererCapability",
            ),
            _optional_string(
                template.get("selectionKey"),
                f"{path}.templates[{index}].selectionKey",
            ),
        )
        for index, raw in enumerate(_list(item.get("templates", []), f"{path}.templates"))
        for template in (_object(raw, f"{path}.templates[{index}]"),)
    )
    return BuildPack(
        _object(item.get("manifest"), f"{path}.manifest"),
        templates,
        _string(item.get("manifestResourceId"), f"{path}.manifestResourceId"),
    )


def _decode_candidate(value: object, path: str) -> PlanningCandidate:
    item = _object(value, path)
    _unknown(
        item,
        {
            "invocationId",
            "packId",
            "selectionKey",
            "templateResourceId",
            "rendererCapability",
            "semanticIds",
            "outputId",
            "outputPath",
            "context",
            "semanticDependencies",
            "artifactDependencies",
            "enabled",
            "skipReason",
            "optionsUsed",
            "bindingsUsed",
            "trace",
        },
        path,
    )
    trace = tuple(
        TraceFact(
            _string(fact.get("kind"), f"{path}.trace[{index}].kind"),
            _string(fact.get("subject"), f"{path}.trace[{index}].subject"),
            _string(fact.get("reason"), f"{path}.trace[{index}].reason"),
        )
        for index, raw in enumerate(_list(item.get("trace", []), f"{path}.trace"))
        for fact in (_object(raw, f"{path}.trace[{index}]"),)
    )
    return PlanningCandidate(
        invocation_id=_string(item.get("invocationId"), f"{path}.invocationId"),
        pack_id=_string(item.get("packId"), f"{path}.packId"),
        selection_key=_string(item.get("selectionKey"), f"{path}.selectionKey"),
        template_resource_id=_string(
            item.get("templateResourceId"),
            f"{path}.templateResourceId",
        ),
        renderer_capability=_string(
            item.get("rendererCapability"),
            f"{path}.rendererCapability",
        ),
        semantic_ids=_strings(item.get("semanticIds", []), f"{path}.semanticIds"),
        output_id=_string(item.get("outputId"), f"{path}.outputId"),
        output_path=_string(item.get("outputPath"), f"{path}.outputPath"),
        context=_object(item.get("context", {}), f"{path}.context"),
        semantic_dependencies=_strings(
            item.get("semanticDependencies", []),
            f"{path}.semanticDependencies",
        ),
        artifact_dependencies=_strings(
            item.get("artifactDependencies", []),
            f"{path}.artifactDependencies",
        ),
        enabled=_bool(item.get("enabled", True), f"{path}.enabled"),
        skip_reason=_optional_string(item.get("skipReason"), f"{path}.skipReason"),
        options_used=_strings(item.get("optionsUsed", []), f"{path}.optionsUsed"),
        bindings_used=_strings(item.get("bindingsUsed", []), f"{path}.bindingsUsed"),
        trace=trace,
    )


def _decode_previous(value: object) -> ManagedOutputManifest:
    outputs = tuple(
        ManagedOutput(
            _string(item.get("path"), f"$.previousManagedOutputs[{index}].path"),
            _string(
                item.get("contentHash"),
                f"$.previousManagedOutputs[{index}].contentHash",
            ),
            _string(
                item.get("ownershipId"),
                f"$.previousManagedOutputs[{index}].ownershipId",
            ),
            _string(
                item.get("artifactId"),
                f"$.previousManagedOutputs[{index}].artifactId",
            ),
        )
        for index, raw in enumerate(_list(value, "$.previousManagedOutputs"))
        for item in (_object(raw, f"$.previousManagedOutputs[{index}]"),)
    )
    return ManagedOutputManifest(tuple(sorted(outputs, key=lambda item: item.path)))


def _decode_snapshot(value: object) -> ProjectSnapshot:
    paths = tuple(
        ProjectPathState(
            _string(item.get("path"), f"$.projectSnapshot[{index}].path"),
            _bool(item.get("exists"), f"$.projectSnapshot[{index}].exists"),
            _optional_string(
                item.get("contentHash"),
                f"$.projectSnapshot[{index}].contentHash",
            ),
        )
        for index, raw in enumerate(_list(value, "$.projectSnapshot"))
        for item in (_object(raw, f"$.projectSnapshot[{index}]"),)
    )
    return ProjectSnapshot(tuple(sorted(paths, key=lambda item: item.path)))


def _connection_id(value: str) -> None:
    if not value or value.strip() != value or any(character.isspace() for character in value):
        raise ApiContractError("API_CONNECTION_ID", "connection id must be a non-empty identifier")


def _object(value: object, path: str) -> dict[str, object]:
    if not isinstance(value, Mapping) or not all(isinstance(key, str) for key in value):
        raise ApiContractError("API_EXPECTED_OBJECT", "expected an object", path=path)
    return dict(value)


def _list(value: object, path: str) -> list[object]:
    if not isinstance(value, list):
        raise ApiContractError("API_EXPECTED_LIST", "expected an array", path=path)
    return value


def _string(value: object, path: str) -> str:
    if not isinstance(value, str) or not value or value.strip() != value:
        raise ApiContractError("API_EXPECTED_STRING", "expected a non-empty trimmed string", path=path)
    return value


def _optional_string(value: object, path: str) -> str | None:
    return None if value is None else _string(value, path)


def _strings(value: object, path: str) -> tuple[str, ...]:
    return tuple(_string(item, path) for item in _list(value, path))


def _bool(value: object, path: str) -> bool:
    if not isinstance(value, bool):
        raise ApiContractError("API_EXPECTED_BOOLEAN", "expected a boolean", path=path)
    return value


def _int(value: object, path: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise ApiContractError("API_EXPECTED_INTEGER", "expected an integer", path=path)
    return value


def _unknown(value: Mapping[str, object], allowed: set[str], path: str) -> None:
    unknown = sorted(set(value) - allowed)
    if unknown:
        raise ApiContractError(
            "API_UNKNOWN_FIELD",
            f"unknown field {unknown[0]!r}",
            path=path,
        )


__all__ = [
    "API_VERSION",
    "ApiContractError",
    "DryvApiService",
    "RegisteredAuthorSession",
    "RegisteredRenderSession",
    "SessionRegistry",
    "encode_build_result",
]
