from importlib.metadata import entry_points

from dryv.ports import (
    IdentifierRole,
    IdentifierValidationRequest,
    ModulePathRequest,
    OutputPathValidationRequest,
)


def test_entry_point_and_authored_syntax_fixture() -> None:
    entry = next(
        item for item in entry_points(group="dryv.language_adapters") if item.name == "dart"
    )
    adapter = entry.load()()
    assert not adapter.validate_identifier(
        IdentifierValidationRequest("User", IdentifierRole.TYPE)
    ).has_errors
    assert not adapter.validate_output_path(
        OutputPathValidationRequest("lib/src/user.dart", "dart")
    ).has_errors
    facts = adapter.resolve_module_path(
        ModulePathRequest(
            "lib/src/service.dart",
            provider_artifact="lib/src/user.dart",
        )
    )
    authored = f"import '{facts.specifier}' show User;"
    assert authored == "import './user.dart' show User;"
    assert not hasattr(facts, "statement")
