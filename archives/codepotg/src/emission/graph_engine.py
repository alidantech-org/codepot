from __future__ import annotations

from collections.abc import Mapping
from dataclasses import replace
from pathlib import Path, PurePosixPath
from typing import Any

from archives.codepotg.src.contracts.emission import (
    EmissionFile,
    EmissionPlan,
    EmissionResult,
    EmissionWriteResult,
)
from archives.codepotg.src.contracts.events import ProgressSink, RuntimeEvent
from archives.codepotg.src.contracts.paths import PathLifecycleMode, PathWritePolicy
from archives.codepotg.src.contracts.template import TemplateDependency, TemplateFile, TemplateGroup
from archives.codepotg.src.core.errors import ConfigError
from archives.codepotg.src.emission.engine import EmissionContextBuilder, import_planner_for_language
from archives.codepotg.src.emission.imports.base import ImportPlanningContext
from archives.codepotg.src.emission.paths.config_loader import load_path_config
from archives.codepotg.src.emission.paths.graph_planner import (
    PathGraphFile,
    PathGraphPlanningError,
    ResolvedSelectionContext,
    plan_path_graph,
)
from archives.codepotg.src.emission.planning import VirtualOutputRegistry
from archives.codepotg.src.emission.templates.renderer import render_template
from archives.codepotg.src.emission.writer.file_writer import write_bytes_if_changed, write_text_if_changed


def emit_graph(
    contract: Any,
    *,
    progress: ProgressSink | None = None,
) -> EmissionResult:
    """Plan and incrementally emit an approved paths selection graph."""

    if contract.emit.template_root is None:
        raise ValueError("template_root is required for emission")
    template_root = contract.emit.template_root
    output_root = contract.emit.output_path
    path_config = load_path_config(template_root, strict=True)
    if not path_config.uses_graph:
        raise ValueError("emit_graph requires a named paths selection/emission graph")

    base_context = EmissionContextBuilder(contract).global_context()
    graph = plan_path_graph(
        config=path_config,
        base_context=base_context,
        template_root=template_root,
    )
    planner = import_planner_for_language(contract.lang.name)
    files = tuple(
        _emission_file(
            graph_file,
            registry=graph.registry,
            template_root=template_root,
            output_root=output_root,
            path_config=path_config,
            import_planner=planner,
            package_name=contract.lang.package.name,
        )
        for graph_file in graph.files
    )
    for index, file in enumerate(files, start=1):
        _notify(
            progress,
            "file_planned",
            f"Planned: {file.output_path}",
            current=index,
            total=len(files),
        )
    plan = EmissionPlan(
        language=contract.lang.name,
        template_root=template_root,
        output_root=output_root,
        files=files,
    )
    return execute_graph_emission(
        plan,
        registry=graph.registry,
        dry_run=contract.emit.dry_run,
        progress=progress,
    )


def execute_graph_emission(
    plan: EmissionPlan,
    *,
    registry: VirtualOutputRegistry,
    dry_run: bool = False,
    progress: ProgressSink | None = None,
) -> EmissionResult:
    """Render and write ready graph files one at a time."""

    refusals = tuple(file for file in plan.files if file.refusal_reason)
    if refusals:
        details = "\n".join(
            f"  - {file.output_path}: {file.refusal_reason}" for file in refusals
        )
        raise ConfigError(f"Unsafe template writes refused:\n{details}")

    if dry_run:
        _notify(
            progress,
            "emission_dry_run",
            f"Dry run skipped {len(plan.files)} files",
            total=len(plan.files),
        )
        return EmissionResult(
            plan=plan,
            write_result=EmissionWriteResult(
                skipped=tuple(file.output_path for file in plan.files),
            ),
            output_registry=registry,
        )

    created: list[Path] = []
    updated: list[Path] = []
    unchanged: list[Path] = []
    skipped: list[Path] = []
    immutable_created: list[Path] = []
    immutable_skipped: list[Path] = []
    completed: set[str] = set()

    for index, file in enumerate(plan.files, start=1):
        relative = PurePosixPath(file.output_path.relative_to(plan.output_root).as_posix())
        missing = tuple(dependency for dependency in file.depends_on if dependency not in completed)
        if missing:
            raise PathGraphPlanningError(
                f"Output '{relative.as_posix()}' was scheduled before dependencies: "
                + ", ".join(missing)
            )

        if file.lifecycle == PathLifecycleMode.IMMUTABLE and file.output_path.exists():
            skipped.append(file.output_path)
            immutable_skipped.append(file.output_path)
            completed.add(relative.as_posix())
            registry.mark_written_path(relative)
            _notify(
                progress,
                "file_immutable_skipped",
                f"Skipped immutable existing: {file.output_path}",
                current=index,
                total=len(plan.files),
            )
            continue

        _notify(
            progress,
            "file_rendering",
            f"Rendering: {file.output_path}",
            current=index,
            total=len(plan.files),
        )
        if file.is_template:
            content = render_template(plan.template_root, file.template_path, file.context)
            _notify(
                progress,
                "file_rendered",
                f"Rendered: {file.output_path}",
                current=index,
                total=len(plan.files),
            )
            result = write_text_if_changed(
                file.output_path,
                content,
                compare_mode=file.compare_mode,
            )
        else:
            source = plan.template_root / file.template_path
            result = write_bytes_if_changed(file.output_path, source.read_bytes())

        _notify(
            progress,
            "file_queued",
            f"Queued for write: {file.output_path}",
            current=index,
            total=len(plan.files),
        )
        created.extend(result.created)
        updated.extend(result.updated)
        unchanged.extend(result.unchanged)
        skipped.extend(result.skipped)
        if file.lifecycle == PathLifecycleMode.IMMUTABLE:
            immutable_created.extend(result.created)

        completed.add(relative.as_posix())
        registry.mark_written_path(relative)
        stage, action = _write_event(result)
        _notify(
            progress,
            stage,
            f"{action}: {file.output_path}",
            current=index,
            total=len(plan.files),
        )

    _notify(
        progress,
        "emission_complete",
        f"Completed {len(plan.files)} graph outputs",
        total=len(plan.files),
    )
    return EmissionResult(
        plan=plan,
        write_result=EmissionWriteResult(
            created=tuple(created),
            updated=tuple(updated),
            unchanged=tuple(unchanged),
            skipped=tuple(skipped),
            immutable_created=tuple(immutable_created),
            immutable_skipped=tuple(immutable_skipped),
        ),
        output_registry=registry,
    )


def _emission_file(
    graph_file: PathGraphFile,
    *,
    registry: VirtualOutputRegistry,
    template_root: Path,
    output_root: Path,
    path_config: Any,
    import_planner: Any,
    package_name: str | None,
) -> EmissionFile:
    relative = PurePosixPath(graph_file.output_path.as_posix())
    output_path = output_root / Path(*relative.parts)
    selected_item = _selected_item(graph_file.context)
    emit = getattr(selected_item, "emit", None)
    template_file = TemplateFile(
        output_path=output_path,
        relative_path=relative,
        name=relative.name,
        stem=relative.stem,
        suffix=relative.suffix,
        depth=max(len(relative.parts) - 1, 0),
        root_prefix=_root_prefix(relative),
        group=emit.group if emit is not None else TemplateGroup.GLOBAL,
        item_key=emit.item_key if emit is not None else None,
        meta={
            "node": graph_file.node_key,
            "selection": graph_file.selection,
            "sourceKey": graph_file.source_key,
            "sourceRef": graph_file.source_ref,
            "resource": graph_file.resource,
            "provides": graph_file.provides,
            "providers": dict(graph_file.providers),
            "barrel": graph_file.is_barrel,
        },
    )
    dependencies, dependency_outputs = _resolve_graph_dependencies(
        graph_file,
        current_file=template_file,
        registry=registry,
        output_root=output_root,
    )
    imports = import_planner.plan_imports(
        ImportPlanningContext(
            current_file=template_file,
            dependencies=dependencies,
            strategy=path_config.imports.strategy,
            output_root=output_root,
            package_name=package_name,
        )
    )
    template_file = replace(template_file, dependencies=dependencies, imports=imports)
    context = dict(graph_file.context)
    context["file"] = template_file
    context["output"] = registry.get_by_path(relative)
    context["provider_outputs"] = {
        purpose: registry.find_emission(
            source,
            resource=graph_file.resource,
        )
        or registry.find_emission(source)
        for purpose, source in graph_file.providers.items()
    }
    refusal_reason = _write_refusal_reason(
        output_path=output_path,
        output_root=output_root,
        lifecycle=graph_file.lifecycle,
        policy=path_config.write_policy,
    )
    return EmissionFile(
        template_path=graph_file.template_path,
        output_path=output_path,
        context=context,
        group=graph_file.node_key,
        is_template=graph_file.template_path.as_posix().endswith(
            path_config.template_extension
        ),
        compare_mode=_compare_mode_for_output(output_path),
        lifecycle=graph_file.lifecycle,
        folder_key=graph_file.node_key,
        refusal_reason=refusal_reason,
        node_key=graph_file.node_key,
        selection=graph_file.selection,
        source_key=graph_file.source_key,
        source_ref=graph_file.source_ref,
        resource=graph_file.resource,
        provides=graph_file.provides,
        provided_symbols=graph_file.provided_symbols,
        providers=dict(graph_file.providers),
        depends_on=graph_file.depends_on,
        dependency_outputs=dependency_outputs,
        is_barrel=graph_file.is_barrel,
    )


def _resolve_graph_dependencies(
    graph_file: PathGraphFile,
    *,
    current_file: TemplateFile,
    registry: VirtualOutputRegistry,
    output_root: Path,
) -> tuple[tuple[TemplateDependency, ...], dict[str, str]]:
    dependencies = _item_dependencies(graph_file.context)
    if not dependencies:
        return (), {}
    configured_sources = set(graph_file.providers.values())
    resolved: list[TemplateDependency] = []
    outputs: dict[str, str] = {}
    for dependency in dependencies:
        target = dependency.target
        is_primitive = bool(target and target.is_primitive)
        if is_primitive:
            resolved.append(
                replace(
                    dependency,
                    exists=True,
                    is_importable=False,
                    meta={**dependency.meta, "reason": "primitive dependency"},
                )
            )
            continue
        candidates = tuple(
            item
            for item in registry.find_ref(dependency.ref)
            if item.emission in configured_sources
            and (
                graph_file.resource is None
                or item.resource is None
                or item.resource == graph_file.resource
            )
        )
        if len(candidates) != 1:
            raise PathGraphPlanningError(
                f"Dependency '{dependency.ref}' for '{graph_file.node_key}' resolved "
                f"{len(candidates)} configured provider outputs."
            )
        candidate = candidates[0]
        provider_path = output_root / Path(*candidate.output_path.parts)
        is_self = candidate.output_path == current_file.relative_path
        if not is_self:
            outputs[dependency.ref] = candidate.output_path.as_posix()
        resolved.append(
            replace(
                dependency,
                exists=True,
                output_path=provider_path,
                relative_path=candidate.output_path,
                is_self=is_self,
                is_importable=not is_self,
                meta={**dependency.meta, "provider": candidate.emission},
            )
        )
    return _unique_dependencies(tuple(resolved)), outputs


def _item_dependencies(context: Mapping[str, Any]) -> tuple[TemplateDependency, ...]:
    selected = context.get("selection")
    if not isinstance(selected, ResolvedSelectionContext):
        return ()
    dependencies: list[TemplateDependency] = []
    for item in selected.items:
        emit = getattr(item, "emit", None)
        dependencies.extend(
            tuple(getattr(emit, "dependencies", ())) if emit is not None else ()
        )
    return tuple(dependencies)


def _selected_item(context: Mapping[str, Any]) -> Any | None:
    selected = context.get("selection")
    if not isinstance(selected, ResolvedSelectionContext) or not selected.items:
        return None
    return selected.item or selected.items[0]


def _unique_dependencies(
    dependencies: tuple[TemplateDependency, ...],
) -> tuple[TemplateDependency, ...]:
    seen: set[tuple[str, str]] = set()
    unique: list[TemplateDependency] = []
    for dependency in dependencies:
        key = (dependency.ref, str(dependency.purpose))
        if key in seen:
            continue
        seen.add(key)
        unique.append(dependency)
    return tuple(unique)


def _root_prefix(relative_path: PurePosixPath) -> str:
    depth = max(len(relative_path.parts) - 1, 0)
    return "." if depth == 0 else "/".join(".." for _ in range(depth))


def _write_refusal_reason(
    *,
    output_path: Path,
    output_root: Path,
    lifecycle: PathLifecycleMode,
    policy: PathWritePolicy,
) -> str:
    if not policy.exists:
        return ""
    try:
        relative = output_path.resolve().relative_to(output_root.resolve())
    except ValueError:
        return f"Target is outside output root: {output_root.resolve()}"
    if _is_under_any(relative, policy.protected_roots):
        return "Target is inside write_policy.protected_roots."
    allowed = (
        policy.managed_roots
        if lifecycle == PathLifecycleMode.MANAGED
        else policy.immutable_roots
    )
    if _is_under_any(relative, allowed):
        return ""
    if lifecycle == PathLifecycleMode.MANAGED:
        return "Managed write is outside write_policy.managed_roots."
    return "Immutable write is outside write_policy.immutable_roots."


def _is_under_any(path: Path, roots: tuple[str, ...]) -> bool:
    return any(_is_under(path, Path(root)) for root in roots)


def _is_under(path: Path, root: Path) -> bool:
    if str(root) in {"", "."}:
        return True
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def _compare_mode_for_output(output_path: Path) -> str:
    if output_path.suffix.lower() in {
        ".dart",
        ".ts",
        ".tsx",
        ".js",
        ".jsx",
        ".py",
        ".java",
        ".go",
        ".rs",
    }:
        return "layout_insensitive"
    return "exact"


def _write_event(result: EmissionWriteResult) -> tuple[str, str]:
    if result.created:
        return "file_written", "Created"
    if result.updated:
        return "file_written", "Updated"
    if result.unchanged:
        return "file_unchanged", "Unchanged"
    return "file_skipped", "Skipped"


def _notify(
    progress: ProgressSink | None,
    stage: str,
    message: str,
    *,
    level: str = "info",
    current: int | None = None,
    total: int | None = None,
) -> None:
    if progress is None:
        return
    progress(
        RuntimeEvent(
            stage=stage,
            message=message,
            level=level,
            current=current,
            total=total,
        )
    )
