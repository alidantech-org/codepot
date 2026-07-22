"""Markdown import/link planner."""

from __future__ import annotations

from contracts.template import TemplateDependency, TemplateImport
from emission.imports.base import ImportPlanningContext
from emission.imports.paths import relative_posix_path, to_posix_path

STYLE_MARKDOWN_LINK = "markdown_link"


class MarkdownImportPlanner:
    """Build relative Markdown links for importable dependencies."""

    def plan_imports(self, context: ImportPlanningContext) -> tuple[TemplateImport, ...]:
        if context.strategy == "none":
            return ()

        imports: list[TemplateImport] = []
        current = to_posix_path(context.current_file.relative_path)

        for dependency in context.dependencies:
            if not dependency.is_importable or dependency.relative_path is None:
                continue

            target = to_posix_path(dependency.relative_path)
            link_path = relative_posix_path(from_file=current, to_file=target)
            label = _dependency_label(dependency)
            imports.append(
                TemplateImport(
                    ref=dependency.ref,
                    label=label,
                    path=link_path,
                    statement=f"- [{label}]({link_path})",
                    style=STYLE_MARKDOWN_LINK,
                    symbols=(label,),
                    dependency=dependency,
                )
            )

        return tuple(imports)


def _dependency_label(dependency: TemplateDependency) -> str:
    if dependency.target and dependency.target.name:
        return dependency.target.name.pascal.o

    return dependency.ref.rsplit("/", 1)[-1] or dependency.ref
