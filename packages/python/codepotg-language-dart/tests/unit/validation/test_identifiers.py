import pytest
from codepotg.diagnostics import DiagnosticSeverity
from codepotg.ports import IdentifierRole, IdentifierValidationRequest
from codepotg_language_dart import (
    DartTargetAdapter,
    DartTargetOptions,
    PrivateIdentifierPolicy,
    UnicodeIdentifierPolicy,
)


@pytest.mark.parametrize("role", list(IdentifierRole))
def test_valid_candidate_for_every_role(role: IdentifierRole) -> None:
    diagnostics = DartTargetAdapter().validate_identifier(
        IdentifierValidationRequest("User_1", role)
    )
    assert not diagnostics.has_errors


@pytest.mark.parametrize(
    ("value", "code"),
    [
        ("", "DART_IDENTIFIER_EMPTY"),
        ("1user", "DART_IDENTIFIER_INVALID"),
        ("user-name", "DART_IDENTIFIER_INVALID"),
        ("user name", "DART_IDENTIFIER_INVALID"),
        ("class", "DART_IDENTIFIER_RESERVED"),
        ("éclair", "DART_IDENTIFIER_UNICODE_UNSUPPORTED"),
    ],
)
def test_invalid_candidates(value: str, code: str) -> None:
    diagnostics = DartTargetAdapter().validate_identifier(
        IdentifierValidationRequest(value, IdentifierRole.VALUE)
    )
    assert code in {item.code for item in diagnostics}


@pytest.mark.parametrize(
    ("value", "severity"),
    [
        ("base", DiagnosticSeverity.INFO),
        ("extension", DiagnosticSeverity.WARNING),
        ("sealed", DiagnosticSeverity.INFO),
        ("mixin", DiagnosticSeverity.WARNING),
        ("required", DiagnosticSeverity.WARNING),
        ("late", DiagnosticSeverity.WARNING),
        ("show", DiagnosticSeverity.INFO),
        ("hide", DiagnosticSeverity.INFO),
        ("deferred", DiagnosticSeverity.WARNING),
    ],
)
def test_contextual_and_builtin_identifiers_are_role_aware(
    value: str,
    severity: DiagnosticSeverity,
) -> None:
    diagnostics = DartTargetAdapter().validate_identifier(
        IdentifierValidationRequest(value, IdentifierRole.VALUE)
    )
    assert {item.code for item in diagnostics} == {"DART_IDENTIFIER_CONTEXTUAL"}
    assert all(item.severity is severity for item in diagnostics)
    assert not diagnostics.has_errors


def test_built_in_identifier_is_rejected_for_type_and_namespace_roles() -> None:
    adapter = DartTargetAdapter()
    for role in (IdentifierRole.TYPE, IdentifierRole.NAMESPACE):
        diagnostics = adapter.validate_identifier(
            IdentifierValidationRequest("mixin", role)
        )
        assert diagnostics.has_errors
        assert {item.code for item in diagnostics} == {"DART_IDENTIFIER_CONTEXTUAL"}


def test_private_name_is_preserved_and_reported() -> None:
    request = IdentifierValidationRequest("_user", IdentifierRole.VALUE)
    diagnostics = DartTargetAdapter().validate_identifier(request)
    assert {item.code for item in diagnostics} == {"DART_IDENTIFIER_PRIVATE"}
    assert not diagnostics.has_errors
    assert request.value == "_user"


def test_strict_public_name_policy_rejects_private_identifier() -> None:
    adapter = DartTargetAdapter(
        DartTargetOptions(
            private_identifier_policy=PrivateIdentifierPolicy.REQUIRE_PUBLIC
        )
    )
    diagnostics = adapter.validate_identifier(
        IdentifierValidationRequest("_user", IdentifierRole.VALUE)
    )
    assert diagnostics.has_errors


def test_spec_validated_unicode_subset() -> None:
    adapter = DartTargetAdapter(
        DartTargetOptions(
            unicode_identifier_policy=UnicodeIdentifierPolicy.SPEC_VALIDATED
        )
    )
    diagnostics = adapter.validate_identifier(
        IdentifierValidationRequest("Éclair", IdentifierRole.TYPE)
    )
    assert not diagnostics.has_errors


def test_diagnostics_are_deterministic() -> None:
    request = IdentifierValidationRequest("1 user", IdentifierRole.PARAMETER)
    adapter = DartTargetAdapter()
    assert adapter.validate_identifier(request) == adapter.validate_identifier(request)
