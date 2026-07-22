"""Resolve template dependencies against planned output files."""

from __future__ import annotations

from dataclasses import replace

from contracts.template import TemplateDependency, TemplateDependencyTargetKind, TemplateFile
from emission.dependencies.output_index import OutputIndex

REASON_MISSING = "target was not emitted"
REASON_PRIMITIVE = "primitive dependency does not require import"
REASON_SELF = "self dependency"


def resolve_file_dependencies(
    *,
    current_file: TemplateFile,
    item_dependencies: tuple[TemplateDependency, ...],
    output_index: OutputIndex,
) -> tuple[TemplateDependency, ...]:
    return tuple(_resolve(current_file, dependency, output_index) for dependency in item_dependencies)


def _resolve(
    current_file: TemplateFile,
    dependency: TemplateDependency,
    output_index: OutputIndex,
) -> TemplateDependency:
    target = dependency.target
    emitted = output_index.find_ref(dependency.ref)
    is_primitive = bool(target and target.kind == TemplateDependencyTargetKind.PRIMITIVE)

    if emitted is None:
        reason = REASON_PRIMITIVE if is_primitive else REASON_MISSING
        return _with_reason(dependency, reason, exists=False, is_importable=False)

    is_self = emitted.relative_path == current_file.relative_path
    if is_self:
        return _with_reason(
            dependency,
            REASON_SELF,
            exists=True,
            is_self=True,
            is_importable=False,
            output_path=emitted.output_path,
            relative_path=emitted.relative_path,
        )

    if is_primitive:
        return _with_reason(
            dependency,
            REASON_PRIMITIVE,
            exists=True,
            is_importable=False,
            output_path=emitted.output_path,
            relative_path=emitted.relative_path,
        )

    return replace(
        dependency,
        exists=True,
        output_path=emitted.output_path,
        relative_path=emitted.relative_path,
        is_self=False,
        is_importable=bool(target and not target.is_primitive),
    )


def _with_reason(dependency: TemplateDependency, reason: str, **changes: object) -> TemplateDependency:
    return replace(dependency, meta={**dependency.meta, "reason": reason}, **changes)
