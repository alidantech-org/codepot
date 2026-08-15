from __future__ import annotations

from dryv.features.artifacts import ManagedOutputManifest, ProjectPathState, ProjectSnapshot, WriteKind
from dryv.features.authoring import (
    AuthorBackendHello,
    AuthorComplete,
    AuthorDocument,
    AuthorRequest,
    AuthorSource,
)
from dryv.features.hashing import HashPurpose, hash_bytes
from dryv.features.packs import PackTemplateResource
from dryv.features.planning import PlanningCandidate, TraceFact
from dryv.features.templating import (
    RenderResult,
    RenderedOutput,
    RendererHello,
)
from dryv.features.serialization import contract_to_json
from dryv.ir import Contract
from dryv.runtime import (
    AuthorSourceBuild,
    AvailableRenderSession,
    BuildPack,
    BuildRequest,
    BuildResource,
    BuildStatus,
    DryvRuntime,
)


class FakeRenderSession:
    def __init__(self, *, renderer_version: str = "1.0.0") -> None:
        self.renderer_version = renderer_version
        self.calls: list[str] = []
        self.cancelled: list[str] = []

    def hello(self) -> RendererHello:
        return RendererHello(
            renderer_id="fake-jinja",
            renderer_version=self.renderer_version,
            capabilities=("jinja/v1",),
            protocol_versions=(1,),
            context_versions=(1,),
            template_media_types=("text/x-jinja-template",),
            fingerprint=f"fake-jinja:{self.renderer_version}",
            max_concurrency=2,
        )

    def render(self, request):
        self.calls.append(request.job_id)
        name = request.context["schema"]["name"]
        content = f"export interface {name} {{}}\n".encode()
        output = request.outputs[0]
        return RenderResult(
            request.job_id,
            self.hello().fingerprint,
            (
                RenderedOutput(
                    output.id,
                    content,
                    hash_bytes(HashPurpose.ARTIFACT_CONTENT, content).identity,
                ),
            ),
        )

    def cancel(self, job_id: str) -> None:
        self.cancelled.append(job_id)


class FakeAuthorSession:
    def __init__(self, document: bytes) -> None:
        self.document = document

    def hello(self) -> AuthorBackendHello:
        return AuthorBackendHello(
            "fake-author",
            "1.0.0",
            ("python",),
            ("1",),
            (1,),
            False,
            "fake-author:1",
        )

    def author(self, request: AuthorRequest):
        yield AuthorDocument("application/vnd.dryv.ir+json", self.document)
        yield AuthorComplete(request.job_id, "fake-author:1")

    def cancel(self, job_id: str) -> None:
        return None


def _pack() -> BuildPack:
    return BuildPack(
        manifest_document={
            "apiVersion": "dryv.dev/v1",
            "id": "example/types",
            "version": "1.0.0",
            "selections": {
                "schemas": {
                    "paths": ["src"],
                    "select": "groups.schemas.objects.each",
                }
            },
        },
        templates=(
            PackTemplateResource(
                "resource://pack/types/templates/schema.jinja",
                "templates/{schemas}/schema.ts.jinja",
                "text/x-jinja-template",
                "jinja/v1",
                "schemas",
            ),
        ),
        manifest_resource_id="resource://pack/types/dryv.pack.yaml",
    )


def _resources() -> tuple[BuildResource, ...]:
    return (
        BuildResource(
            "resource://pack/types/dryv.pack.yaml",
            "application/yaml",
            b"apiVersion: dryv.dev/v1\nid: example/types\nversion: 1.0.0\n",
        ),
        BuildResource(
            "resource://pack/types/templates/schema.jinja",
            "text/x-jinja-template",
            b"export interface {{ schema.name }} {}",
        ),
    )


def _candidate() -> PlanningCandidate:
    return PlanningCandidate(
        invocation_id="invocation.user-type",
        pack_id="example/types",
        selection_key="schemas",
        template_resource_id="resource://pack/types/templates/schema.jinja",
        renderer_capability="jinja/v1",
        semantic_ids=("identity.schema.user",),
        output_id="artifact.user-type",
        output_path="src/user.ts",
        context={"schema": {"id": "identity.schema.user", "name": "User"}},
        semantic_dependencies=("identity.schema.user",),
        trace=(TraceFact("selection", "identity.schema.user", "matched schemas selection"),),
    )


def _request(
    contract: Contract,
    renderer: FakeRenderSession,
    *,
    previous: ManagedOutputManifest = ManagedOutputManifest(),
    snapshot: ProjectSnapshot | None = None,
) -> BuildRequest:
    return BuildRequest(
        build_id="build.user",
        resources=_resources(),
        planning_candidates=(_candidate(),),
        packs=(_pack(),),
        precompiled_contract=contract,
        render_sessions=(AvailableRenderSession("renderer.local", renderer),),
        previous_managed_outputs=previous,
        project_snapshot=snapshot
        or ProjectSnapshot((ProjectPathState("src/user.ts", False),)),
    )


def test_runtime_composes_precompiled_ir_to_write_instructions(connected_contract: Contract) -> None:
    renderer = FakeRenderSession()
    result = DryvRuntime().build(_request(connected_contract, renderer))

    assert result.success
    assert result.status is BuildStatus.RENDER_COMPLETE
    assert result.artifacts is not None
    assert result.artifacts.instructions[0].kind is WriteKind.CREATE
    assert result.artifacts.artifacts[0].path == "src/user.ts"
    assert renderer.calls == ["invocation.user-type"]
    assert {item.stage for item in result.trace} >= {
        "ir",
        "pack",
        "planning",
        "render-dispatch",
        "render-result",
        "artifact",
    }


def test_repeated_build_reuses_context_and_render_cache(connected_contract: Contract) -> None:
    renderer = FakeRenderSession()
    runtime = DryvRuntime()
    first = runtime.build(_request(connected_contract, renderer))
    assert first.success and first.artifacts is not None

    managed = first.artifacts.next_manifest
    current_hash = first.artifacts.artifacts[0].content_hash
    second = runtime.build(
        _request(
            connected_contract,
            renderer,
            previous=managed,
            snapshot=ProjectSnapshot((ProjectPathState("src/user.ts", True, current_hash),)),
        )
    )
    assert second.success
    assert second.cache.context_hits == 1
    assert second.cache.render_hits == 1
    assert renderer.calls == ["invocation.user-type"]
    assert second.artifacts is not None
    assert second.artifacts.instructions[0].kind is WriteKind.UNCHANGED


def test_renderer_fingerprint_change_invalidates_render_cache(connected_contract: Contract) -> None:
    runtime = DryvRuntime()
    first_renderer = FakeRenderSession(renderer_version="1.0.0")
    first = runtime.build(_request(connected_contract, first_renderer))
    assert first.success and first.artifacts is not None

    second_renderer = FakeRenderSession(renderer_version="2.0.0")
    artifact = first.artifacts.artifacts[0]
    second = runtime.build(
        _request(
            connected_contract,
            second_renderer,
            previous=first.artifacts.next_manifest,
            snapshot=ProjectSnapshot((ProjectPathState("src/user.ts", True, artifact.content_hash),)),
        )
    )
    assert second.success
    assert second.cache.render_misses == 1
    assert second_renderer.calls == ["invocation.user-type"]


def test_author_session_source_uses_same_runtime_pipeline(connected_contract: Contract) -> None:
    renderer = FakeRenderSession()
    author = FakeAuthorSession(contract_to_json(connected_contract, pretty=False).encode())
    request = BuildRequest(
        build_id="build.author",
        resources=_resources(),
        planning_candidates=(_candidate(),),
        packs=(_pack(),),
        author=AuthorSourceBuild(
            AuthorRequest(
                1,
                "author.job",
                "1",
                "python",
                (AuthorSource("resource://project/author.py", "text/x-python"),),
            ),
            author,
        ),
        render_sessions=(AvailableRenderSession("renderer.local", renderer),),
        project_snapshot=ProjectSnapshot((ProjectPathState("src/user.ts", False),)),
    )
    result = DryvRuntime().build(request)
    assert result.success
    assert any(item.stage == "authoring" for item in result.trace)


def test_render_failure_never_reports_render_complete_or_commits_false_success(
    connected_contract: Contract,
) -> None:
    class BrokenRenderer(FakeRenderSession):
        def render(self, request):
            raise ValueError("template exploded")

    runtime = DryvRuntime()
    result = runtime.build(_request(connected_contract, BrokenRenderer()))
    assert not result.success
    assert not result.render_complete
    assert result.status is BuildStatus.FAILED
