from codepotg.ports import OutputPathValidationRequest

from codepotg_language_typescript import create_plugin
from codepotg_language_typescript.targets import match_typescript_suffix


def test_targets_and_longest_suffixes() -> None:
    adapter = create_plugin()
    assert tuple(target.id for target in adapter.targets) == (
        "typescript",
        "typescript-jsx",
    )
    assert match_typescript_suffix("types.d.ts") == ".d.ts"
    assert match_typescript_suffix("types.d.mts") == ".d.mts"
    assert match_typescript_suffix("types.d.cts") == ".d.cts"
    for path, target in [
        ("src/a.ts", "typescript"),
        ("src/a.tsx", "typescript-jsx"),
        ("src/a.mts", "typescript"),
        ("src/a.cts", "typescript"),
    ]:
        assert not adapter.validate_output_path(
            OutputPathValidationRequest(path, target)
        ).has_errors


def test_target_mismatch_and_unknown() -> None:
    adapter = create_plugin()
    assert adapter.validate_output_path(
        OutputPathValidationRequest("src/a.ts", "typescript-jsx")
    ).has_errors
    diagnostics = adapter.validate_output_path(OutputPathValidationRequest("src/a.ts", "unknown"))
    assert {diagnostic.code for diagnostic in diagnostics} == {"TS_TARGET_UNKNOWN"}
