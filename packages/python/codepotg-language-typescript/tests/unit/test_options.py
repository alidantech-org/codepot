from dataclasses import FrozenInstanceError

import pytest
from codepotg_language_typescript import (
    AliasBinding,
    IndexResolutionPolicy,
    ReservedWordPolicy,
    TypeScriptExtensionPolicy,
    TypeScriptTargetAdapter,
    TypeScriptTargetOptions,
    UnicodeIdentifierPolicy,
)
from codepotg_language_typescript.modules.policies import apply_path_policies


def test_options_are_immutable_serializable_and_strict() -> None:
    options = TypeScriptTargetOptions.from_mapping(
        {"aliases": [{"alias": "@", "root": "src"}]}
    )
    assert options.to_dict()["aliases"] == ({"alias": "@", "root": "src"},)
    with pytest.raises(FrozenInstanceError):
        options.package_name = "x"  # type: ignore[misc]
    with pytest.raises(ValueError, match="unknown TypeScript option"):
        TypeScriptTargetOptions.from_mapping({"quote_style": "single"})
    with pytest.raises(ValueError, match="must be a mapping"):
        TypeScriptTargetOptions.from_mapping([])  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("reserved_word_policy", "warning", "reserved_word_policy"),
        ("unicode_identifier_policy", "specValidated", "unicode_identifier_policy"),
        ("extension_policy", "omitTypeScript", "extension_policy"),
        ("index_policy", "omitIndex", "index_policy"),
        ("reserved_word_policy", 1, "reserved_word_policy"),
        ("unicode_identifier_policy", True, "unicode_identifier_policy"),
    ],
)
def test_direct_options_reject_non_enum_policy_values(
    field: str,
    value: object,
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        TypeScriptTargetOptions(**{field: value})  # type: ignore[arg-type]


@pytest.mark.parametrize("package_name", [1, True, object()])
def test_direct_options_reject_non_string_package_names(package_name: object) -> None:
    with pytest.raises(ValueError, match="package_name must be a string or null"):
        TypeScriptTargetOptions(package_name=package_name)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "aliases",
    [
        [AliasBinding("@a", "src")],
        ({"alias": "@a", "root": "src"},),
        (object(),),
    ],
)
def test_direct_options_reject_invalid_alias_collections(aliases: object) -> None:
    with pytest.raises(ValueError, match="TS_MODULE_ALIAS_INVALID"):
        TypeScriptTargetOptions(aliases=aliases)  # type: ignore[arg-type]


def test_alias_binding_rejects_invalid_direct_scalar_types() -> None:
    with pytest.raises(ValueError, match="alias and root must be strings"):
        AliasBinding(1, "src")  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="alias and root must be strings"):
        AliasBinding("@", 1)  # type: ignore[arg-type]


def test_valid_direct_enum_policies_control_extension_and_index_behavior() -> None:
    preserved = TypeScriptTargetOptions(
        reserved_word_policy=ReservedWordPolicy.WARNING,
        unicode_identifier_policy=UnicodeIdentifierPolicy.SPEC_VALIDATED,
        extension_policy=TypeScriptExtensionPolicy.PRESERVE,
        index_policy=IndexResolutionPolicy.PRESERVE,
    )
    assert apply_path_policies("src/index.ts", preserved) == "src/index.ts"
    assert preserved.to_dict()["extension_policy"] == "preserve"

    omitted = TypeScriptTargetOptions(
        extension_policy=TypeScriptExtensionPolicy.OMIT_TYPESCRIPT,
        index_policy=IndexResolutionPolicy.OMIT_INDEX,
    )
    assert apply_path_policies("src/index.ts", omitted) == "src"


def test_alias_duplicates_rejected() -> None:
    with pytest.raises(ValueError):
        TypeScriptTargetOptions(
            aliases=(AliasBinding("@a", "src"), AliasBinding("@b", "src"))
        )


def test_adapter_instance_is_immutable_and_rejects_invalid_options() -> None:
    adapter = TypeScriptTargetAdapter()
    with pytest.raises(FrozenInstanceError):
        adapter.options = adapter.options  # type: ignore[misc]
    with pytest.raises(ValueError, match="TypeScriptTargetOptions"):
        TypeScriptTargetAdapter(options={})  # type: ignore[arg-type]
