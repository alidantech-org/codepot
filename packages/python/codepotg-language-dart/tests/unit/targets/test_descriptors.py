from codepotg.ports import OutputPathValidationRequest
from codepotg_language_dart import create_plugin


def test_target_descriptor_is_sorted_and_valid() -> None:
    adapter = create_plugin()
    assert tuple(target.id for target in adapter.targets) == ("dart",)
    target = adapter.targets[0]
    assert target.aliases == ()
    assert target.extensions == (".dart",)
    assert tuple(sorted(set(target.capabilities))) == target.capabilities
    assert not adapter.validate_output_path(
        OutputPathValidationRequest("lib/src/user.dart", "dart")
    ).has_errors


def test_unknown_target_and_wrong_extension() -> None:
    adapter = create_plugin()
    diagnostics = adapter.validate_output_path(
        OutputPathValidationRequest("lib/src/user.dart", "unknown")
    )
    assert {diagnostic.code for diagnostic in diagnostics} == {"DART_TARGET_UNKNOWN"}
    assert adapter.validate_output_path(
        OutputPathValidationRequest("lib/src/user.ts", "dart")
    ).has_errors
