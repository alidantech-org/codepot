from __future__ import annotations

from dataclasses import replace
from pathlib import Path, PurePosixPath

from codepotg.config import (
    PackInstanceConfig,
    PackManifest,
    ProjectConfig,
    SelectionConfig,
    load_pack_manifest,
)
from codepotg.diagnostics import Diagnostic, Diagnostics, DiagnosticSeverity
from codepotg.domain.generation import DEFAULT_SELECTOR_REGISTRY, SelectionContext, SelectorRegistry
from codepotg.ir import Contract, validate_contract
from codepotg.ports import ModulePathRequest, OutputPathValidationRequest
from codepotg.runtime.plugins import PluginLoadError, RuntimePlugins

from .context import RenderContextBuilder
from .discovery import PackDiscoveryError, discover_pack_files
from .expressions import ExpressionError, evaluate_text
from .models import (
    ArtifactPlan,
    DiscoveredPackFile,
    GenerationPlan,
    ModuleCollection,
    ModuleDescriptor,
    PackFileKind,
)


class ProjectPlanner:
    def __init__(
        self,
        *,
        plugins: RuntimePlugins,
        selectors: SelectorRegistry = DEFAULT_SELECTOR_REGISTRY,
    ) -> None:
        self._plugins = plugins
        self._selectors = selectors

    def plan(
        self,
        *,
        project: ProjectConfig,
        project_root: str | Path,
        contracts: dict[str, Contract],
    ) -> GenerationPlan:
        root = Path(project_root)
        diagnostics: list[Diagnostic] = []
        artifacts: list[ArtifactPlan] = []

        for instance in project.packs:
            try:
                planned = self._plan_pack(
                    project=project,
                    project_root=root,
                    instance=instance,
                    contracts=contracts,
                )
                artifacts.extend(planned)
            except (ValueError, PackDiscoveryError, PluginLoadError, ExpressionError) as exc:
                diagnostics.append(_exception_diagnostic(exc, instance.name))

        unique: list[ArtifactPlan] = []
        paths: dict[str, ArtifactPlan] = {}
        ids: set[str] = set()
        for artifact in sorted(artifacts, key=lambda item: (item.output_path, item.id)):
            previous = paths.get(artifact.output_path)
            if previous is not None:
                diagnostics.append(
                    _error(
                        "PLAN_OUTPUT_COLLISION",
                        "several planned artifacts resolve to the same output path",
                        path=artifact.output_path,
                        first=previous.id,
                        second=artifact.id,
                    )
                )
                continue
            if artifact.id in ids:
                diagnostics.append(
                    _error(
                        "PLAN_ARTIFACT_ID_COLLISION",
                        "several planned artifacts use the same identity",
                        artifact=artifact.id,
                    )
                )
                continue
            paths[artifact.output_path] = artifact
            ids.add(artifact.id)
            unique.append(artifact)

        return GenerationPlan(
            project_name=project.name,
            artifacts=tuple(unique),
            diagnostics=Diagnostics.from_iterable(diagnostics),
        )

    def _plan_pack(
        self,
        *,
        project: ProjectConfig,
        project_root: Path,
        instance: PackInstanceConfig,
        contracts: dict[str, Contract],
    ) -> tuple[ArtifactPlan, ...]:
        if instance.source.local is None:
            raise ValueError(
                "PACK_PROVIDER_UNSUPPORTED: the first orchestrator supports local packs only"
            )
        pack_root = (project_root / instance.source.local).resolve()
        manifest = load_pack_manifest(pack_root / "CodepotgPack.yaml")
        options = manifest.resolve_options(instance.options)
        manifest.validate_bindings(instance.bindings)
        files = discover_pack_files(pack_root, manifest, self._plugins)
        partials = self._partials(files)

        contract: Contract | None = None
        if instance.input is not None:
            contract = contracts.get(instance.input)
            if contract is None:
                raise ValueError(
                    f"PLAN_INPUT_MISSING: source {instance.input!r} was not normalized"
                )
            semantic_diagnostics = validate_contract(contract)
            if semantic_diagnostics.has_errors:
                first = semantic_diagnostics.errors[0]
                raise ValueError(f"{first.code}: {first.message}")

        initial: list[ArtifactPlan] = []
        for file in files:
            if file.kind is PackFileKind.PARTIAL:
                continue
            selection = (
                manifest.selection(file.selection_key)
                if file.selection_key not in {None, "root"}
                else None
            )
            contexts = self._selection_contexts(selection, contract)
            if not contexts:
                contexts = (None,)
            for context in contexts:
                initial.append(
                    self._artifact(
                        project=project,
                        instance=instance,
                        manifest=manifest,
                        file=file,
                        selection=selection,
                        context=context,
                        contract=contract,
                        options=options,
                        partials=partials,
                    )
                )

        return self._resolve_dependencies(initial, manifest)

    def _selection_contexts(
        self,
        selection: SelectionConfig | None,
        contract: Contract | None,
    ) -> tuple[SelectionContext, ...]:
        if selection is None or selection.select is None:
            return ()
        if contract is None:
            raise ValueError(
                "PLAN_SELECTION_INPUT_REQUIRED: semantic selections require a pack input"
            )
        try:
            return self._selectors.select(selection.select, contract)
        except KeyError as exc:
            raise ValueError(
                f"PLAN_SELECTOR_UNKNOWN: unknown fixed selector {selection.select!r}"
            ) from exc

    def _artifact(
        self,
        *,
        project: ProjectConfig,
        instance: PackInstanceConfig,
        manifest: PackManifest,
        file: DiscoveredPackFile,
        selection: SelectionConfig | None,
        context: SelectionContext | None,
        contract: Contract | None,
        options: tuple[tuple[str, object], ...],
        partials: tuple[tuple[str, str], ...],
    ) -> ArtifactPlan:
        semantic_id = _semantic_id(context)
        group_id = str(context.group.id) if context is not None and context.group is not None else None
        identity = ":".join(
            part
            for part in (
                instance.name,
                file.selection_key or "literal",
                semantic_id or "once",
                file.pack_path,
            )
            if part
        )
        provisional = ArtifactPlan(
            id=identity,
            pack_instance=instance.name,
            pack_id=manifest.id,
            selection_key=file.selection_key,
            template_id=file.pack_path,
            output_path="pending",
            kind=file.kind,
            context=context,
            semantic_id=semantic_id,
            group_id=group_id,
            engine_id=file.engine_id,
            target_id=file.target_id,
            partials=partials,
            content=file.content,
        )
        if file.kind is PackFileKind.TEMPLATE and contract is None:
            raise ValueError(
                "PLAN_TEMPLATE_INPUT_REQUIRED: rendered templates require a semantic input"
            )
        render_context = (
            RenderContextBuilder(contract).build(
                selection=context,
                project=project,
                manifest=manifest,
                artifact=provisional,
                options=options,
                bindings=instance.bindings,
            )
            if contract is not None
            else tuple(sorted((
                ("bindings", instance.bindings),
                ("options", options),
                ("pack", (("id", manifest.id), ("version", manifest.version))),
                ("project", (("name", project.name),)),
            )))
        )
        output_path = _output_path(instance, selection, file, render_context)
        symbols = tuple(
            evaluate_text(symbol, render_context) for symbol in (selection.symbols if selection else ())
        )
        artifact = replace(
            provisional,
            output_path=output_path,
            symbols=symbols,
        )
        _validate_target_path(artifact, self._plugins)
        return artifact

    def _resolve_dependencies(
        self,
        artifacts: list[ArtifactPlan],
        manifest: PackManifest,
    ) -> tuple[ArtifactPlan, ...]:
        providers: dict[str, tuple[ArtifactPlan, ...]] = {}
        for selection in manifest.selections:
            providers[selection.key] = tuple(
                item for item in artifacts if item.selection_key == selection.key
            )

        resolved: list[ArtifactPlan] = []
        for artifact in artifacts:
            selection = (
                manifest.selection(artifact.selection_key)
                if artifact.selection_key not in {None, "root"}
                else None
            )
            if selection is None:
                resolved.append(artifact)
                continue
            imports = tuple(
                (
                    local_name,
                    ModuleCollection(
                        self._modules(
                            consumer=artifact,
                            target_key=target_key,
                            candidates=providers.get(target_key, ()),
                        )
                    ),
                )
                for local_name, target_key in selection.imports
            )
            exports = tuple(
                (
                    target_key,
                    ModuleCollection(
                        self._modules(
                            consumer=artifact,
                            target_key=target_key,
                            candidates=providers.get(target_key, ()),
                        )
                    ),
                )
                for target_key in sorted(selection.exports)
            )
            resolved.append(replace(artifact, imports=imports, exports=exports))
        return tuple(resolved)

    def _modules(
        self,
        *,
        consumer: ArtifactPlan,
        target_key: str,
        candidates: tuple[ArtifactPlan, ...],
    ) -> tuple[ModuleDescriptor, ...]:
        matched = _match_providers(consumer, candidates)
        if not matched:
            raise ValueError(
                f"PLAN_PROVIDER_MISSING: selection {target_key!r} has no matching artifact"
            )
        if consumer.target_id is None:
            raise ValueError(
                "PLAN_TARGET_REQUIRED: generated dependencies require a target adapter"
            )
        adapter = self._plugins.target(consumer.target_id)
        modules: list[ModuleDescriptor] = []
        for provider in matched:
            if provider.target_id != consumer.target_id:
                raise ValueError(
                    "PLAN_TARGET_MISMATCH: generated dependencies must share a target"
                )
            facts = adapter.resolve_module_path(
                ModulePathRequest(
                    current_artifact=consumer.output_path,
                    provider_artifact=provider.output_path,
                )
            )
            modules.append(
                ModuleDescriptor(
                    selection_key=target_key,
                    artifact_path=provider.output_path,
                    specifier=facts.specifier,
                    symbols=provider.symbols,
                    semantic_id=provider.semantic_id,
                )
            )
        return tuple(sorted(modules, key=lambda item: (item.specifier, item.artifact_path)))

    @staticmethod
    def _partials(files: tuple[DiscoveredPackFile, ...]) -> tuple[tuple[str, str], ...]:
        partials: list[tuple[str, str]] = []
        for file in files:
            if file.kind is not PackFileKind.PARTIAL:
                continue
            try:
                source = file.content.decode("utf-8")
            except UnicodeDecodeError as exc:
                raise ValueError(
                    f"PACK_PARTIAL_ENCODING: partial {file.pack_path!r} is not UTF-8"
                ) from exc
            partials.append((file.pack_path, source))
        return tuple(sorted(partials))


def _output_path(
    instance: PackInstanceConfig,
    selection: SelectionConfig | None,
    file: DiscoveredPackFile,
    context: tuple[tuple[str, object], ...],
) -> str:
    parts = list(PurePosixPath(file.pack_path).parts)
    parts = [part for part in parts if not (part.startswith("{") and part.endswith("}"))]
    if file.engine_suffix is not None:
        parts[-1] = parts[-1][: -len(file.engine_suffix)]
    prefix = list(PurePosixPath(instance.output).parts)
    if selection is not None:
        prefix.extend(selection.paths)
    rendered = evaluate_text("/".join((*prefix, *parts)), context)
    if not rendered or rendered.startswith("/") or "\\" in rendered:
        raise ValueError("PLAN_OUTPUT_PATH_INVALID: output paths must be POSIX-relative")
    path = PurePosixPath(rendered)
    if any(part in {"", ".", ".."} for part in path.parts):
        raise ValueError(
            "PLAN_OUTPUT_PATH_INVALID: output paths cannot contain dot or traversal segments"
        )
    return path.as_posix()


def _validate_target_path(artifact: ArtifactPlan, plugins: RuntimePlugins) -> None:
    if artifact.target_id is None:
        return
    adapter = plugins.target(artifact.target_id)
    diagnostics = adapter.validate_output_path(
        OutputPathValidationRequest(
            path=artifact.output_path,
            target_id=artifact.target_id,
        )
    )
    if diagnostics.has_errors:
        first = diagnostics.errors[0]
        raise ValueError(f"{first.code}: {first.message}")


def _semantic_id(context: SelectionContext | None) -> str | None:
    if context is None:
        return None
    selected = context.selected
    value = getattr(getattr(selected, "id", None), "value", None)
    return value if isinstance(value, str) else None


def _match_providers(
    consumer: ArtifactPlan,
    candidates: tuple[ArtifactPlan, ...],
) -> tuple[ArtifactPlan, ...]:
    candidates = tuple(item for item in candidates if item.id != consumer.id)
    if consumer.semantic_id is not None:
        exact = tuple(item for item in candidates if item.semantic_id == consumer.semantic_id)
        if exact:
            return exact
    if consumer.group_id is not None:
        scoped = tuple(item for item in candidates if item.group_id == consumer.group_id)
        if scoped:
            return scoped
    return candidates


def _exception_diagnostic(exc: Exception, pack_instance: str) -> Diagnostic:
    code = getattr(exc, "code", None)
    if not isinstance(code, str):
        text = str(exc)
        code = text.split(":", 1)[0] if ":" in text else "PLAN_FAILED"
    message = getattr(exc, "message", None)
    if not isinstance(message, str):
        message = str(exc) or "pack planning failed"
    return _error(code, message, pack_instance=pack_instance)


def _error(code: str, message: str, **details: object) -> Diagnostic:
    return Diagnostic(
        code=code,
        severity=DiagnosticSeverity.ERROR,
        message=message,
        details=tuple(sorted(details.items())),
    )
