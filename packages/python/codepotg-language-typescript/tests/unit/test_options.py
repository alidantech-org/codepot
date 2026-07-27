from dataclasses import FrozenInstanceError

import pytest
from codepotg_language_typescript import AliasBinding, TypeScriptTargetOptions


def test_options_are_immutable_serializable_and_strict() -> None:
    options = TypeScriptTargetOptions.from_mapping(
        {"aliases": [{"alias": "@", "root": "src"}]}
    )
    assert options.to_dict()["aliases"] == ({"alias": "@", "root": "src"},)
    with pytest.raises(FrozenInstanceError):
        options.package_name = "x"  # type: ignore[misc]
    with pytest.raises(ValueError, match="unknown TypeScript option"):
        TypeScriptTargetOptions.from_mapping({"quote_style": "single"})


def test_alias_duplicates_rejected() -> None:
    with pytest.raises(ValueError):
        TypeScriptTargetOptions(
            aliases=(AliasBinding("@a", "src"), AliasBinding("@b", "src"))
        )


def test_adapter_instance_is_immutable() -> None:
    from codepotg_language_typescript import TypeScriptTargetAdapter

    adapter = TypeScriptTargetAdapter()
    with pytest.raises(FrozenInstanceError):
        adapter.options = adapter.options  # type: ignore[misc]
