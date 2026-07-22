"""Markdown import planner tests."""

from __future__ import annotations

from pathlib import Path

from contracts.names import make_contract_name
from contracts.template import TemplateDependency, TemplateDependencyTarget, TemplateDependencyTargetKind, TemplateFile
from emission.imports.base import ImportPlanningContext
from emission.imports.markdown import MarkdownImportPlanner

USER_REF = "#/components/schemas/User"


def test_markdown_import_relative_link_same_resource(tmp_path: Path) -> None:
    imports = _plan("docs/resources/users/schemas/models/user.md", "docs/resources/users/schemas/enums/status.md")

    assert imports[0].path == "../enums/status.md"
    assert imports[0].statement == "- [User](../enums/status.md)"


def test_markdown_import_relative_link_shared_resource(tmp_path: Path) -> None:
    imports = _plan("docs/resources/platform/auth/users/schemas/models/user.md", "docs/resources/shared/schemas/models/base.md")

    assert imports[0].path == "../../../../../shared/schemas/models/base.md"


def test_markdown_import_uses_posix_separators_on_windows_paths(tmp_path: Path) -> None:
    imports = _plan(r"docs\resources\users\schemas\models\user.md", r"docs\resources\users\schemas\dtos\body.md")

    assert imports[0].path == "../dtos/body.md"


def test_markdown_import_skips_non_importable_dependencies(tmp_path: Path) -> None:
    dependency = _dependency("docs/user.md", importable=False)
    current = TemplateFile(tmp_path / "docs/current.md", Path("docs/current.md"), "current.md", "current", ".md")

    imports = MarkdownImportPlanner().plan_imports(
        ImportPlanningContext(current_file=current, dependencies=(dependency,), strategy="relative")
    )

    assert imports == ()


def _plan(current: str, target: str):
    dependency = _dependency(target)
    file = TemplateFile(Path(current), Path(current), Path(current).name, Path(current).stem, ".md")
    return MarkdownImportPlanner().plan_imports(
        ImportPlanningContext(current_file=file, dependencies=(dependency,), strategy="relative")
    )


def _dependency(relative: str, importable: bool = True) -> TemplateDependency:
    return TemplateDependency(
        ref=USER_REF,
        target=TemplateDependencyTarget(ref=USER_REF, name=make_contract_name("User"), kind=TemplateDependencyTargetKind.MODEL),
        is_importable=importable,
        exists=True,
        relative_path=Path(relative),
    )
