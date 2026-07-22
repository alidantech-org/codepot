"""Dependency resolver tests."""

from __future__ import annotations

from pathlib import Path

from contracts.names import make_contract_name
from contracts.template import (
    TemplateDependency,
    TemplateDependencyPurpose,
    TemplateDependencyTarget,
    TemplateDependencyTargetKind,
    TemplateFile,
)
from emission.dependencies.output_index import EmittedItem, OutputIndex
from emission.dependencies.resolver import REASON_MISSING, REASON_PRIMITIVE, REASON_SELF, resolve_file_dependencies

USER_REF = "#/components/schemas/User"


def test_resolves_emitted_model_dependency(tmp_path: Path) -> None:
    dependency = _dependency(USER_REF, TemplateDependencyTargetKind.MODEL)

    resolved = _resolve(tmp_path, dependency)

    assert resolved.exists is True
    assert resolved.is_importable is True
    assert resolved.relative_path.as_posix() == "docs/user.md"


def test_marks_primitive_dependency_not_importable(tmp_path: Path) -> None:
    dependency = _dependency("#/components/schemas/String", TemplateDependencyTargetKind.PRIMITIVE)

    resolved = _resolve(tmp_path, dependency, index=OutputIndex(by_ref={}, by_key={}))

    assert resolved.exists is False
    assert resolved.is_importable is False
    assert resolved.meta["reason"] == REASON_PRIMITIVE


def test_marks_self_dependency_not_importable(tmp_path: Path) -> None:
    dependency = _dependency(USER_REF, TemplateDependencyTargetKind.MODEL)

    resolved = _resolve(tmp_path, dependency, current_relative="docs/user.md")

    assert resolved.exists is True
    assert resolved.is_self is True
    assert resolved.is_importable is False
    assert resolved.meta["reason"] == REASON_SELF


def test_marks_missing_dependency_exists_false(tmp_path: Path) -> None:
    dependency = _dependency("#/components/schemas/Missing", TemplateDependencyTargetKind.MODEL)

    resolved = _resolve(tmp_path, dependency, index=OutputIndex(by_ref={}, by_key={}))

    assert resolved.exists is False
    assert resolved.is_importable is False
    assert resolved.meta["reason"] == REASON_MISSING


def test_marks_inheritance_dependency(tmp_path: Path) -> None:
    dependency = _dependency(USER_REF, TemplateDependencyTargetKind.MODEL, inheritance=True)

    resolved = _resolve(tmp_path, dependency)

    assert resolved.is_inheritance is True
    assert resolved.is_importable is True


def _resolve(tmp_path: Path, dependency: TemplateDependency, current_relative: str = "docs/current.md", index=None):
    current = TemplateFile(tmp_path / current_relative, Path(current_relative), "current.md", "current", ".md")
    return resolve_file_dependencies(
        current_file=current,
        item_dependencies=(dependency,),
        output_index=index or _index(tmp_path),
    )[0]


def _dependency(ref: str, kind: TemplateDependencyTargetKind, inheritance: bool = False) -> TemplateDependency:
    return TemplateDependency(
        ref=ref,
        purpose=TemplateDependencyPurpose.INHERITANCE if inheritance else TemplateDependencyPurpose.FIELD_TYPE,
        target=TemplateDependencyTarget(ref=ref, name=make_contract_name("User"), kind=kind, is_primitive=kind == TemplateDependencyTargetKind.PRIMITIVE),
        is_inheritance=inheritance,
    )


def _index(tmp_path: Path) -> OutputIndex:
    file = TemplateFile(tmp_path / "docs/user.md", Path("docs/user.md"), "user.md", "user", ".md")
    item = EmittedItem(USER_REF, USER_REF, None, None, make_contract_name("User"), "User", file.output_path, file.relative_path, file)
    return OutputIndex(by_ref={USER_REF: item}, by_key={})
