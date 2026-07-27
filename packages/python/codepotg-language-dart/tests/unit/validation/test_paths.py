import pytest
from codepotg.ports import OutputPathValidationRequest
from codepotg_language_dart import create_plugin


@pytest.mark.parametrize(
    "path",
    [
        "lib/src/user.dart",
        "bin/tool.dart",
        "test/user_test.dart",
        "tool/generate.dart",
        "example/example.dart",
    ],
)
def test_valid_non_framework_paths(path: str) -> None:
    diagnostics = create_plugin().validate_output_path(
        OutputPathValidationRequest(path, "dart")
    )
    assert not diagnostics.has_errors


@pytest.mark.parametrize(
    "path",
    [
        "",
        "../user.dart",
        "/lib/user.dart",
        "C:/lib/user.dart",
        "//server/share/user.dart",
        "lib\\user.dart",
        "lib/./user.dart",
        "lib/a/../user.dart",
        "lib/CON.dart",
        "lib/user .dart",
        "lib/user.dart.",
        "lib/user.ts",
    ],
)
def test_rejected_paths(path: str) -> None:
    diagnostics = create_plugin().validate_output_path(
        OutputPathValidationRequest(path, "dart")
    )
    assert diagnostics.has_errors
