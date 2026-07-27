from dataclasses import FrozenInstanceError

import pytest
from codepotg.diagnostics import DiagnosticSeverity
from codepotg.ports import IdentifierRole, IdentifierValidationRequest
from codepotg_language_dart import (
    DartTargetAdapter,
    DartTargetOptions,
    PrivateIdentifierPolicy,
    ReservedWordPolicy,
    UnicodeIdentifierPolicy,
)


def test_options_are_immutable_serializable_and_strict() -> None:
    options = DartTargetOptions.from_mapping(
        {"package_name": "example_sdk", "prefer_package_uris": True}
    )
    assert options.to_dict()["package_name"] == "example_sdk"
    assert options.to_dict()["prefer_package_uris"] is True
    with pytest.raises(FrozenInstanceError):
        options.package_name = "other"  # type: ignore[misc]
    with pytest.raises(ValueError, match="unknown Dart option"):
        DartTargetOptions.from_mapping({"annotation_style": "generated"})
    with pytest.raises(ValueError, match="must be a mapping"):
        DartTargetOptions.from_mapping([])  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("reserved_word_policy", "warning", "reserved_word_policy"),
        ("unicode_identifier_policy", "specValidated", "unicode_identifier_policy"),
        ("private_identifier_policy", "requirePublic", "private_identifier_policy"),
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
        DartTargetOptions(**{field: value})  # type: ignore[arg-type]


@pytest.mark.parametrize("package_name", [1, True, object()])
def test_direct_options_reject_non_string_package_names(package_name: object) -> None:
    with pytest.raises(ValueError, match="package_name must be a string or null"):
        DartTargetOptions(package_name=package_name)  # type: ignore[arg-type]


@pytest.mark.parametrize("prefer_package_uris", [0, 1, "true", None])
def test_direct_options_reject_non_boolean_package_uri_preference(
    prefer_package_uris: object,
) -> None:
    with pytest.raises(ValueError, match="prefer_package_uris must be a boolean"):
        DartTargetOptions(
            prefer_package_uris=prefer_package_uris  # type: ignore[arg-type]
        )


def test_valid_direct_enum_policies_preserve_privacy_and_keyword_behavior() -> None:
    options = DartTargetOptions(
        reserved_word_policy=ReservedWordPolicy.WARNING,
        unicode_identifier_policy=UnicodeIdentifierPolicy.SPEC_VALIDATED,
        private_identifier_policy=PrivateIdentifierPolicy.REQUIRE_PUBLIC,
    )
    adapter = DartTargetAdapter(options)

    private_diagnostics = adapter.validate_identifier(
        IdentifierValidationRequest("_user", IdentifierRole.VALUE)
    )
    assert private_diagnostics.has_errors
    assert {item.code for item in private_diagnostics} == {"DART_IDENTIFIER_PRIVATE"}

    reserved_diagnostics = adapter.validate_identifier(
        IdentifierValidationRequest("class", IdentifierRole.VALUE)
    )
    assert not reserved_diagnostics.has_errors
    assert {item.code for item in reserved_diagnostics} == {"DART_IDENTIFIER_RESERVED"}
    assert all(
        item.severity is DiagnosticSeverity.WARNING for item in reserved_diagnostics
    )
    assert options.to_dict()["private_identifier_policy"] == "requirePublic"


def test_invalid_package_name_rejected() -> None:
    with pytest.raises(ValueError, match="valid Dart package name"):
        DartTargetOptions(package_name="Example-SDK")


def test_adapter_instance_is_immutable_and_rejects_invalid_options() -> None:
    adapter = DartTargetAdapter()
    with pytest.raises(FrozenInstanceError):
        adapter.options = adapter.options  # type: ignore[misc]
    with pytest.raises(ValueError, match="DartTargetOptions"):
        DartTargetAdapter(options={})  # type: ignore[arg-type]
