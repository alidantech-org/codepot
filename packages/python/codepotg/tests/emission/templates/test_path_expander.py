"""Tests for template path expansion."""

from __future__ import annotations

from pathlib import Path

from src.contracts.names import make_contract_name
from src.emission.templates.path_expander import expand_template_path


def test_expand_template_path_strips_final_j2(tmp_path) -> None:
    schema_name = make_contract_name("User")
    output = expand_template_path(
        Path("schemas/[schema.name.path.o]/schema.txt.j2"),
        {"schema": {"name": schema_name}},
    )

    assert output.as_posix() == "schemas/user/schema.txt"


def test_expand_template_path_keeps_raw_file_extension(tmp_path) -> None:
    output = expand_template_path(
        Path(".gitignore"),
        {},
    )

    assert output.as_posix() == ".gitignore"


def test_expands_dynamic_file_name():
    context = {
        "version": "v1",
        "name": make_contract_name("UserProfiles"),
    }

    result = expand_template_path(
        Path("lib/[version]/[name.path]_model.dart.j2"),
        context,
    )

    assert result.as_posix() == "lib/v1/user_profiles_model.dart"


def test_expands_escaped_nextjs_segment():
    result = expand_template_path(
        Path("app/[[...slug]]/page.tsx.j2"),
        {},
    )

    assert result.as_posix() == "app/[...slug]/page.tsx"


def test_expands_escaped_folder_segment():
    result = expand_template_path(
        Path("docs/{{not-a-folder}}/page.txt.j2"),
        {},
    )

    assert result.as_posix() == "docs/{not-a-folder}/page.txt"


def test_original_is_default_for_name_case():
    context = {
        "schema": {"name": make_contract_name("UserProfiles")},
    }

    result = expand_template_path(
        Path("[schema.name.path.o]/model.dart.j2"),
        context,
    )

    assert result.as_posix() == "user_profiles/model.dart"


def test_dynamic_sequence_expands_to_nested_path():
    result = expand_template_path(
        Path("res/[path]/[name.path]/resource.txt.j2"),
        {
            "path": ("platform", "auth"),
            "name": make_contract_name("users"),
        },
    )

    assert result.as_posix() == "res/platform/auth/users/resource.txt"
