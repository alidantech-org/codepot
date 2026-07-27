from importlib.metadata import entry_points

import pytest
from codepotg.ports import (
    IdentifierRole,
    IdentifierValidationRequest,
    ModulePathRequest,
    OutputPathValidationRequest,
)


def test_dual_entry_points_when_both_wheels_are_installed() -> None:
    entries = {entry.name: entry for entry in entry_points(group="codepotg.language_adapters")}
    if not {"typescript", "dart"} <= entries.keys():
        pytest.skip("combined TypeScript and Dart wheel environment is not installed")

    typescript = entries["typescript"].load()()
    dart = entries["dart"].load()()

    assert typescript.plugin.id == "typescript"
    assert dart.plugin.id == "dart"
    assert {target.id for target in typescript.targets} == {
        "typescript",
        "typescript-jsx",
    }
    assert {target.id for target in dart.targets} == {"dart"}

    assert not typescript.validate_identifier(
        IdentifierValidationRequest("User", IdentifierRole.TYPE)
    ).has_errors
    assert not typescript.validate_output_path(
        OutputPathValidationRequest("src/user.ts", "typescript")
    ).has_errors
    assert (
        typescript.resolve_module_path(
            ModulePathRequest("src/service.ts", provider_artifact="src/user.ts")
        ).specifier
        == "./user"
    )

    assert not dart.validate_identifier(
        IdentifierValidationRequest("User", IdentifierRole.TYPE)
    ).has_errors
    assert not dart.validate_output_path(
        OutputPathValidationRequest("lib/src/user.dart", "dart")
    ).has_errors
    assert (
        dart.resolve_module_path(
            ModulePathRequest(
                "lib/src/service.dart",
                provider_artifact="lib/src/user.dart",
            )
        ).specifier
        == "./user.dart"
    )
