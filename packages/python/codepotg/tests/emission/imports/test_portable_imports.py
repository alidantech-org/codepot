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

CASES = (
    (
        ".py",
        "package/src/portable_client/models/widget.py",
        "package/src/portable_client/models/widget_status.py",
        "from .widget_status import WidgetStatus",
    ),
    (
        ".java",
        "package/src/main/java/generated/models/widget.java",
        "package/src/main/java/generated/models/widget_status.java",
        "import generated.models.WidgetStatus;",
    ),
    (
        ".cs",
        "package/Models/widget.cs",
        "package/Models/widget_status.cs",
        "using Models;",
    ),
    (
        ".go",
        "package/models/widget.go",
        "package/models/widget_status.go",
        'import "portable-client/models"',
    ),
    (
        ".rs",
        "package/src/models/widget.rs",
        "package/src/models/widget_status.rs",
        "use crate::models::widget_status::WidgetStatus;",
    ),
)


@pytest.mark.parametrize(
    ("suffix", "current_path", "target_path", "statement"),
    CASES,
)
def test_fallback_planner_builds_portable_source_imports(
    suffix: str,
    current_path: str,
    target_path: str,
    statement: str,
) -> None:
    current_relative = PurePosixPath(current_path)
    current = TemplateFile(
        output_path=Path(current_path),
        relative_path=current_relative,
        name=current_relative.name,
        stem=current_relative.stem,
        suffix=suffix,
        group=TemplateGroup.MODELS,
    )
    dependency = TemplateDependency(
        ref="#/components/schemas/WidgetStatus",
        target=TemplateDependencyTarget(
            ref="#/components/schemas/WidgetStatus",
            name=make_contract_name("WidgetStatus"),
        ),
        relative_path=Path(target_path),
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
        output_path=Path("package/src/portable_client/models/widget.py"),
        relative_path=PurePosixPath(
            "package/src/portable_client/models/widget.py"
        ),
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
        relative_path=Path(
            "package/src/portable_client/models/widget_status.py"
        ),
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


def test_portable_import_planner_respects_none_strategy() -> None:
    current = TemplateFile(
        output_path=Path("package/src/models/widget.rs"),
        relative_path=PurePosixPath("package/src/models/widget.rs"),
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
