"""Emission engine for template rendering and file writing.

The engine consumes TemplateContract and produces rendered files. It does not
know about concrete language implementations, OpenAPI documents, or inference.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

from archives.codepotg.src.contracts.emission import (
    EmissionFile,
    EmissionPlan,
    EmissionResult,
    EmissionWriteResult,
    TemplateContext,
)
from archives.codepotg.src.contracts.events import ProgressSink, RuntimeEvent
from archives.codepotg.src.contracts.paths import PathLifecycleMode, PathWritePolicy
from archives.codepotg.src.contracts.template import TemplateContract, TemplateDependency, TemplateFile, TemplateGroup
from archives.codepotg.src.core.errors import ConfigError
from archives.codepotg.src.emission.dependencies.output_index import build_output_index
from archives.codepotg.src.emission.dependencies.resolver import resolve_file_dependencies
from archives.codepotg.src.emission.imports.base import ImportPlanner, ImportPlanningContext
from archives.codepotg.src.emission.imports.markdown import MarkdownImportPlanner
from archives.codepotg.src.emission.imports.paths import to_posix_path
from archives.codepotg.src.emission.paths.config_loader import load_path_config
from archives.codepotg.src.emission.paths.selection import (
    CONTEXT_FOLDER_NAME,
    CONTEXT_FOLDER_PARTS,
    expand_folder_contexts,
)
from archives.codepotg.src.emission.templates.descriptor import TemplateDescriptor
from archives.codepotg.src.emission.templates.path_expander import expand_template_path
from archives.codepotg.src.emission.templates.renderer import render_template
from archives.codepotg.src.emission.templates.scanner import scan_templates
from archives.codepotg.src.emission.writer.file_writer import write_text_if_changed

GROUP_GLOBAL = "global"


def import_planner_for_language(language_name: str) -> ImportPlanner:
    """Return the appropriate import planner for a language."""
    if language_name == "dart":
        from archives.codepotg.src.languages.dart.imports import DartImportPlanner

        return DartImportPlanner()
        
    if language_name in {"typescript", "ts"}:
        from archives.codepotg.src.languages.typescript.imports import TypeScriptImportPlanner

        return TypeScriptImportPlanner()

    return MarkdownImportPlanner()


@dataclass
class _DependencyStats:
    resolved: int = 0
    importable: int = 0
    primitive: int = 0
    missing: int = 0
    self_skipped: int = 0
    inheritance: int = 0

    def add(self, dependencies: tuple[TemplateDependency, ...]) -> None:
        for dependency in dependencies:
            self.resolved += 1
            self.importable += int(dependency.is_importable)
            self.self_skipped += int(dependency.is_self)
            self.inheritance += int(dependency.is_inheritance)
            self.missing += int(not dependency.exists)
            self.primitive += int(bool(dependency.target and dependency.target.is_primitive))


@dataclass(frozen=True)
class EmissionContextBuilder:
    """Builds base template contexts from a TemplateContract."""

    contract: TemplateContract

    def global_context(self) -> TemplateContext:
        """Build the global template context.

        Folder recipes from paths.yaml enrich this context with selected aliases
        and resolved output folder parts.
        """
        return {
            "project": self.contract.project,
            "api": self.contract.api,
            "lang": self.contract.lang,
            "emit": self.contract.emit,
            "meta": self.contract.meta,
            "resources": self.contract.resources,
            "features": self.contract.features,
            "schemas": self.contract.schemas,
            "operations": self.contract.operations,
            "entities": self.contract.entities,
            "frontends": self.contract.frontends,
            "selected_frontend": self.contract.selected_frontend,
            "selected_frontends": self.contract.selected_frontends,
            "frontend_count": self.contract.frontend_count,
            "file": self.contract.file,
        }


def emit(
    contract: TemplateContract,
    *,
    progress: ProgressSink | None = None,
) -> EmissionResult:
    """Plan and execute emission in one step."""
    plan = build_emission_plan(contract, progress=progress)
    return execute_emission(
        plan,
        dry_run=contract.emit.dry_run,
        progress=progress,
    )


def build_emission_plan(
    contract: TemplateContract,
    *,
    progress: ProgressSink | None = None,
) -> EmissionPlan:
    """Build an emission plan from a template contract without writing files."""
    if contract.emit.template_root is None:
        raise ValueError("template_root is required for emission")

    template_root = contract.emit.template_root
    output_root = contract.emit.output_path

    _notify(progress, "loading_path_config", f"Loading path config from {template_root}")
    path_config = load_path_config(template_root)

    _notify(progress, "scanning_templates", f"Scanning templates in {template_root}")
    descriptors = scan_templates(template_root)

    base_context = EmissionContextBuilder(contract).global_context()
    files: list[EmissionFile] = []

    for descriptor in descriptors:
        for context in _contexts_for_descriptor(descriptor, base_context, path_config):
            output_path = _resolve_output_path(
                descriptor=descriptor,
                context=context,
                output_root=output_root,
                template_extension=path_config.template_extension,
            )
            context = _context_with_file(
                descriptor=descriptor,
                context=context,
                output_path=output_path,
                output_root=output_root,
                path_config=path_config,
            )
            folder_key = _descriptor_folder_key(descriptor)
            lifecycle = _lifecycle_for_folder(folder_key, path_config)
            refusal_reason = _write_refusal_reason(
                output_path=output_path,
                output_root=output_root,
                lifecycle=lifecycle,
                policy=path_config.write_policy,
            )

            files.append(
                EmissionFile(
                    template_path=descriptor.relative_path,
                    output_path=output_path,
                    context=context,
                    content=None,
                    group=_descriptor_group(descriptor),
                    is_template=_is_jinja_template(
                        descriptor.relative_path,
                        template_extension=path_config.template_extension,
                    ),
                    compare_mode=_compare_mode_for_output(output_path),
                    lifecycle=lifecycle,
                    folder_key=folder_key,
                    refusal_reason=refusal_reason,
                )
            )

    files = _resolve_file_contexts(
        files=files,
        output_root=output_root,
        path_config=path_config,
        progress=progress,
        contract=contract,
    )
    files = [
        replace(
            file,
            content=_resolve_content(file.template_path, template_root, file.context),
        )
        for file in files
    ]

    _notify(
        progress,
        "emission_plan_created",
        f"Planned {len(files)} files",
        total=len(files),
    )

    return EmissionPlan(
        language=contract.lang.name,
        template_root=template_root,
        output_root=output_root,
        files=tuple(files),
    )


def execute_emission(
    plan: EmissionPlan,
    *,
    dry_run: bool = False,
    progress: ProgressSink | None = None,
) -> EmissionResult:
    """Execute an emission plan by writing files unless dry-run is enabled."""
    if dry_run:
        refused = tuple(file.output_path for file in plan.files if file.refusal_reason)
        if refused:
            reasons = {
                file.output_path: file.refusal_reason for file in plan.files if file.refusal_reason
            }
            details = "\n".join(f"  - {path}: {reasons[path]}" for path in refused)
            raise ConfigError(f"Unsafe template writes refused:\n{details}")
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
        )

    created: list[Path] = []
    updated: list[Path] = []
    unchanged: list[Path] = []
    skipped: list[Path] = []
    immutable_created: list[Path] = []
    immutable_skipped: list[Path] = []
    refused: list[Path] = []
    refusal_reasons: dict[Path, str] = {}

    for index, file in enumerate(plan.files, start=1):
        _notify(
            progress,
            "rendering_file",
            f"Rendering: {file.output_path}",
            current=index,
            total=len(plan.files),
        )

        if file.refusal_reason:
            refused.append(file.output_path)
            refusal_reasons[file.output_path] = file.refusal_reason
            _notify(
                progress,
                "file_refused",
                f"Refused unsafe {file.lifecycle.value} write: {file.output_path}",
                level="error",
                current=index,
                total=len(plan.files),
            )
            continue

        if file.lifecycle == PathLifecycleMode.IMMUTABLE and file.output_path.exists():
            skipped.append(file.output_path)
            immutable_skipped.append(file.output_path)
            _notify(
                progress,
                "file_immutable_skipped",
                f"Skipped immutable existing: {file.output_path}",
                current=index,
                total=len(plan.files),
            )
            continue

        if file.is_template:
            if not isinstance(file.content, str):
                raise TypeError(f"Template content must be string: {file.template_path}")

            result = write_text_if_changed(
                file.output_path,
                file.content,
                compare_mode=file.compare_mode,
            )
        else:
            result = _write_raw_file(
                source_path=plan.template_root / file.template_path,
                output_path=file.output_path,
            )

        created.extend(result.created)
        updated.extend(result.updated)
        unchanged.extend(result.unchanged)
        skipped.extend(result.skipped)
        if file.lifecycle == PathLifecycleMode.IMMUTABLE:
            immutable_created.extend(result.created)

        for path in result.created:
            label = (
                "Created immutable"
                if file.lifecycle == PathLifecycleMode.IMMUTABLE
                else "Created managed"
            )
            _notify(
                progress,
                "file_created",
                f"{label}: {path}",
                current=index,
                total=len(plan.files),
            )
        for path in result.updated:
            _notify(
                progress,
                "file_updated",
                f"Updated managed: {path}",
                current=index,
                total=len(plan.files),
            )
        for path in result.unchanged:
            _notify(
                progress,
                "file_unchanged",
                f"Unchanged managed: {path}",
                current=index,
                total=len(plan.files),
            )
        for path in result.skipped:
            _notify(
                progress,
                "file_skipped",
                f"Skipped: {path}",
                current=index,
                total=len(plan.files),
            )

    if refused:
        details = "\n".join(f"  - {path}: {refusal_reasons[path]}" for path in refused)
        raise ConfigError(f"Unsafe template writes refused:\n{details}")

    return EmissionResult(
        plan=plan,
        write_result=EmissionWriteResult(
            created=tuple(created),
            updated=tuple(updated),
            unchanged=tuple(unchanged),
            skipped=tuple(skipped),
            immutable_created=tuple(immutable_created),
            immutable_skipped=tuple(immutable_skipped),
            refused=tuple(refused),
            refusal_reasons=refusal_reasons,
        ),
    )


def _contexts_for_descriptor(
    descriptor: TemplateDescriptor,
    base_context: TemplateContext,
    path_config: Any,
) -> tuple[TemplateContext, ...]:
    """Build render contexts for a descriptor using folder recipe segments."""
    folder_names = tuple(token.expression for token in descriptor.folders)

    if not folder_names:
        return (dict(base_context),)

    return expand_folder_contexts(
        base_context=base_context,
        folder_name=folder_names[0],
        path_config=path_config,
    )


def _resolve_output_path(
    *,
    descriptor: TemplateDescriptor,
    context: TemplateContext,
    output_root: Path,
    template_extension: str,
) -> Path:
    output_template = Path(*_output_parts_for_context(descriptor, context))
    expanded = expand_template_path(
        output_template,
        context,
        template_extension=template_extension,
    )
    return output_root / expanded


def _resolve_content(
    template_path: Path,
    template_root: Path,
    context: TemplateContext,
) -> str | bytes | None:
    if _is_jinja_template(template_path):
        return render_template(template_root, template_path, context)

    return None


def _context_with_file(
    *,
    descriptor: TemplateDescriptor,
    context: TemplateContext,
    output_path: Path,
    output_root: Path,
    path_config: Any,
) -> TemplateContext:
    current = _selected_item(context, path_config)
    emit = getattr(current, "emit", None)
    relative_path = to_posix_path(output_path.relative_to(output_root))
    suffix = "".join(relative_path.suffixes[-1:])
    template_file = TemplateFile(
        output_path=output_path,
        relative_path=relative_path,
        name=relative_path.name,
        stem=relative_path.stem,
        suffix=suffix,
        depth=max(len(relative_path.parts) - 1, 0),
        root_prefix=_root_prefix(relative_path),
        group=emit.group if emit is not None else TemplateGroup.GLOBAL,
        item_key=emit.item_key if emit is not None else None,
    )
    bound = dict(context)
    bound["file"] = template_file
    return bound


def _resolve_file_contexts(
    *,
    files: list[EmissionFile],
    output_root: Path,
    path_config: Any,
    progress: ProgressSink | None,
    contract: TemplateContract,
) -> list[EmissionFile]:
    output_index = build_output_index(files, output_root)
    planner = import_planner_for_language(contract.lang.name)
    resolved_files: list[EmissionFile] = []
    stats = _DependencyStats()

    for file in files:
        template_file = file.context.get("file")
        if not isinstance(template_file, TemplateFile):
            resolved_files.append(file)
            continue

        dependencies = resolve_file_dependencies(
            current_file=template_file,
            item_dependencies=_item_dependencies(file.context, path_config),
            output_index=output_index,
        )
        imports = planner.plan_imports(
            ImportPlanningContext(
                current_file=template_file,
                dependencies=dependencies,
                strategy=path_config.imports.strategy,
                output_root=output_root,
                package_name=contract.lang.package.name,
            )
        )
        stats.add(dependencies)
        next_file = replace(template_file, dependencies=dependencies, imports=imports)
        next_context = {**file.context, "file": next_file}
        resolved_files.append(replace(file, context=next_context))

    _notify_dependency_stats(progress, stats)
    return resolved_files


def _selected_item(context: TemplateContext, path_config: Any) -> Any:
    folder_name = context.get(CONTEXT_FOLDER_NAME)
    if not folder_name:
        return None

    folder = path_config.folder_by_name().get(folder_name)
    if folder is None:
        return None

    return context.get(folder.alias)


def _item_dependencies(
    context: TemplateContext,
    path_config: Any,
) -> tuple[TemplateDependency, ...]:
    item = _selected_item(context, path_config)
    dependencies = _dependencies_from_item(item)
    return _unique_dependencies(dependencies)


def _dependencies_from_item(item: Any) -> tuple[TemplateDependency, ...]:
    emit = getattr(item, "emit", None)
    return tuple(getattr(emit, "dependencies", ()))


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


def _root_prefix(relative_path: Any) -> str:
    depth = max(len(relative_path.parts) - 1, 0)
    return "." if depth == 0 else "/".join(".." for _ in range(depth))


def _notify_dependency_stats(progress: ProgressSink | None, stats: _DependencyStats) -> None:
    _notify(
        progress,
        "dependencies_resolved",
        "Resolved dependencies: "
        f"{stats.resolved}; Importable dependencies: {stats.importable}; "
        f"Primitive dependencies skipped: {stats.primitive}; "
        f"Missing dependency targets: {stats.missing}; "
        f"Self dependencies skipped: {stats.self_skipped}; "
        f"Inheritance dependencies: {stats.inheritance}",
    )


def _write_raw_file(*, source_path: Path, output_path: Path) -> EmissionWriteResult:
    """Write a raw file with byte-level changed detection."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    new_content = source_path.read_bytes()

    if output_path.exists() and output_path.read_bytes() == new_content:
        return EmissionWriteResult(unchanged=(output_path,))

    if output_path.exists():
        output_path.write_bytes(new_content)
        return EmissionWriteResult(updated=(output_path,))

    output_path.write_bytes(new_content)
    return EmissionWriteResult(created=(output_path,))


def _descriptor_group(descriptor: TemplateDescriptor) -> str:
    """Return a display group for the descriptor."""
    if not descriptor.folders:
        return GROUP_GLOBAL

    return descriptor.folders[-1].expression


def _descriptor_folder_key(descriptor: TemplateDescriptor) -> str:
    if not descriptor.folders:
        return GROUP_GLOBAL
    return descriptor.folders[-1].expression


def _lifecycle_for_folder(folder_key: str, path_config: Any) -> PathLifecycleMode:
    if not path_config.write_policy.exists:
        return PathLifecycleMode.MANAGED

    folder = path_config.folder_by_name().get(folder_key)
    if folder is not None and folder.lifecycle is not None:
        return folder.lifecycle
    return path_config.write_policy.default_mode


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

    allowed_roots = (
        policy.managed_roots
        if lifecycle == PathLifecycleMode.MANAGED
        else policy.immutable_roots
    )
    if _is_under_any(relative, allowed_roots):
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


def _output_parts_for_context(
    descriptor: TemplateDescriptor,
    context: TemplateContext,
) -> tuple[str, ...]:
    output_parts: list[str] = []

    for segment in descriptor.segments:
        if segment.is_folder:
            output_parts.extend(str(part) for part in context.get(CONTEXT_FOLDER_PARTS, ()))
            continue

        output_parts.append(segment.raw)

    return tuple(output_parts)


def _is_jinja_template(path: Path, template_extension: str = ".j2") -> bool:
    return path.as_posix().endswith(template_extension)


def _compare_mode_for_output(output_path: Path) -> str:
    suffix = output_path.suffix.lower()

    if suffix in {".dart", ".ts", ".tsx", ".js", ".jsx", ".py", ".java", ".go", ".rs"}:
        return "layout_insensitive"

    return "exact"


def _notify(
    progress: ProgressSink | None,
    stage: str,
    message: str,
    *,
    level: str = "info",
    current: int | None = None,
    total: int | None = None,
) -> None:
    """Emit a progress event."""
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
