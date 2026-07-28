"""TypeScript import planner tests."""

from __future__ import annotations

from pathlib import Path

from contracts.names import make_contract_name
from contracts.template import (
    TemplateDependency,
    TemplateDependencyTarget,
    TemplateDependencyTargetKind,
    TemplateFile,
)
from emission.imports.base import ImportPlanningContext
from languages.typescript.imports import TypeScriptImportPlanner

USER_REF = "#/components/schemas/User"


def test_typescript_relative_import_keeps_same_folder_dot_slash() -> None:
    imports = _plan(
        "lib/server/types/users/dto/user_response.ts",
        "lib/server/types/users/dto/user_public.ts",
    )

    assert imports[0].path == "./user_public"
    assert imports[0].statement == "import { User } from './user_public';"


def _plan(current: str, target: str):
    dependency = TemplateDependency(
        ref=USER_REF,
        target=TemplateDependencyTarget(
            ref=USER_REF,
            name=make_contract_name("User"),
            kind=TemplateDependencyTargetKind.DTO,
        ),
        is_importable=True,
        exists=True,
        relative_path=Path(target),
    )
    file = TemplateFile(Path(current), Path(current), Path(current).name, Path(current).stem, ".ts")
    return TypeScriptImportPlanner().plan_imports(
        ImportPlanningContext(
            current_file=file,
            dependencies=(dependency,),
            strategy="relative",
            package_name="api",
        )
    )
