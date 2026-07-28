"""Import planning coverage for the five additional source languages."""

from __future__ import annotations

from pathlib import Path, PurePosixPath

import pytest

from contracts.names import make_contract_name
from contracts.template import (
    TemplateDependency,
    TemplateDependencyTarget,
    TemplateFile,
    TemplateGroup,
)
from emission.imports.base import ImportPlanningContext
from emission.imports.markdown import MarkdownImportPlanner


@pytest.mark.parametrize(
    ("suffix", "target_parent", "statement"),
    (
        (".py", "native/schemas", "from .widget_status import WidgetStatus"),
        (".java", "native/schemas", "import native.schemas.WidgetStatus;"),
        (".cs", "native/schemas", "using Generated.Native.Schemas;"),
        (
            ".go",
            "native/enums",
            'import "example.com/generated/portable_client/native/enums"',
        ),
        (".rs", "native/schemas", "use crate::native::schemas::widget_status::WidgetStatus;"),
    ),
)
def test_fallback_planner_builds_portable_source_imports(
    suffix: str,
    target_parent: str,
    statement: str,
) -> None:
    current = TemplateFile(
        output_path=Path(f"native/schemas/widget{suffix}"),
        relative_path=PurePosixPath(f"native/schemas/widget{suffix}"),
        name=f"widget{suffix}",
        stem="widget",
        suffix=suffix,
        group=TemplateGroup.MODELS,
    )
    dependency = TemplateDependency(
        ref="#/components/schemas/WidgetStatus",
        target=TemplateDependencyTarget(
            ref="#/components/schemas/WidgetStatus",
            name=make_contract_name("WidgetStatus"),
        ),
        relative_path=Path(f"{target_parent}/widget_status{suffix}"),
        is_importable=True,
        exists=True,
    )

    imports = MarkdownImportPlanner().plan_imports(
        ImportPlanningContext(
            current_file=current,
            dependencies=(dependency,),
            strategy="relative",
            package_name="portable_client",
        )
    )

    assert len(imports) == 1
    assert imports[0].statement == statement
    assert imports[0].symbols == ("WidgetStatus",)
    assert imports[0].dependency is dependency


def test_portable_import_planner_deduplicates_statements() -> None:
    current = TemplateFile(
        output_path=Path("native/schemas/widget.py"),
        relative_path=PurePosixPath("native/schemas/widget.py"),
        name="widget.py",
        stem="widget",
        suffix=".py",
    )
    dependency = TemplateDependency(
        ref="#/components/schemas/WidgetStatus",
        target=TemplateDependencyTarget(
            ref="#/components/schemas/WidgetStatus",
            name=make_contract_name("WidgetStatus"),
        ),
        relative_path=Path("native/schemas/widget_status.py"),
        is_importable=True,
        exists=True,
    )

    imports = MarkdownImportPlanner().plan_imports(
        ImportPlanningContext(
            current_file=current,
            dependencies=(dependency, dependency),
            strategy="relative",
        )
    )

    assert len(imports) == 1


def test_go_import_planner_skips_same_package_dependencies() -> None:
    current = TemplateFile(
        output_path=Path("package/models/widget.go"),
        relative_path=PurePosixPath("package/models/widget.go"),
        name="widget.go",
        stem="widget",
        suffix=".go",
    )
    dependency = TemplateDependency(
        ref="#/components/schemas/WidgetStatus",
        target=TemplateDependencyTarget(
            ref="#/components/schemas/WidgetStatus",
            name=make_contract_name("WidgetStatus"),
        ),
        relative_path=Path("package/models/widget_status.go"),
        is_importable=True,
        exists=True,
    )

    imports = MarkdownImportPlanner().plan_imports(
        ImportPlanningContext(
            current_file=current,
            dependencies=(dependency,),
            strategy="relative",
            package_name="portable_client",
        )
    )

    assert imports == ()


def test_portable_import_planner_respects_none_strategy() -> None:
    current = TemplateFile(
        output_path=Path("native/schemas/widget.rs"),
        relative_path=PurePosixPath("native/schemas/widget.rs"),
        name="widget.rs",
        stem="widget",
        suffix=".rs",
    )

    imports = MarkdownImportPlanner().plan_imports(
        ImportPlanningContext(
            current_file=current,
            dependencies=(),
            strategy="none",
        )
    )

    assert imports == ()
