import pytest
from dryv.ports import OutputPathValidationRequest

from dryv_language_typescript import create_plugin


@pytest.mark.parametrize(
    "path",
    [
        "src/user.ts",
        "src/user.tsx",
        "src/user.mts",
        "src/user.cts",
        "src/user.d.ts",
        "src/user.d.mts",
        "src/user.d.cts",
    ],
)
def test_valid_paths(path: str) -> None:
    target = "typescript-jsx" if path.endswith(".tsx") else "typescript"
    diagnostics = create_plugin().validate_output_path(OutputPathValidationRequest(path, target))
    assert not diagnostics.has_errors


@pytest.mark.parametrize(
    "path",
    [
        "",
        "../user.ts",
        "/src/user.ts",
        "C:/src/user.ts",
        "//server/share/user.ts",
        "src\\user.ts",
        "src/./user.ts",
        "src/a/../user.ts",
        "src/CON.ts",
        "src/user .ts",
        "src/user.ts.",
    ],
)
def test_rejected_paths(path: str) -> None:
    diagnostics = create_plugin().validate_output_path(
        OutputPathValidationRequest(path, "typescript")
    )
    assert diagnostics.has_errors


def test_declaration_requires_basename() -> None:
    diagnostics = create_plugin().validate_output_path(
        OutputPathValidationRequest("src/.d.ts", "typescript")
    )
    assert "TS_FILE_DECLARATION_INVALID" in {diagnostic.code for diagnostic in diagnostics}
