from importlib.metadata import entry_points

from dryv.ports import (
    IdentifierRole,
    IdentifierValidationRequest,
    ModulePathRequest,
    OutputPathValidationRequest,
)


def test_entry_point_and_authored_syntax_fixture() -> None:
    entry = next(
        item
        for item in entry_points(group="dryv.language_adapters")
        if item.name == "typescript"
    )
    adapter = entry.load()()
    assert not adapter.validate_identifier(
        IdentifierValidationRequest("User", IdentifierRole.TYPE)
    ).has_errors
    assert not adapter.validate_output_path(
        OutputPathValidationRequest("src/user.ts", "typescript")
    ).has_errors
    facts = adapter.resolve_module_path(
        ModulePathRequest("src/service.ts", provider_artifact="src/user.ts")
    )
    authored = f'import type {{ User }} from "{facts.specifier}";'
    assert authored == 'import type { User } from "./user";'
    assert not hasattr(facts, "statement")
