import pytest
from codepotg.ports import IdentifierRole, IdentifierValidationRequest

from codepotg_language_typescript import (
    TypeScriptTargetAdapter,
    TypeScriptTargetOptions,
    UnicodeIdentifierPolicy,
)


@pytest.mark.parametrize("role", list(IdentifierRole))
def test_valid_candidate_for_every_role(role: IdentifierRole) -> None:
    diagnostics = TypeScriptTargetAdapter().validate_identifier(
        IdentifierValidationRequest("User_1", role)
    )
    assert not diagnostics.has_errors


@pytest.mark.parametrize(
    ("value", "code"),
    [
        ("", "TS_IDENTIFIER_EMPTY"),
        ("1user", "TS_IDENTIFIER_INVALID"),
        ("user-name", "TS_IDENTIFIER_INVALID"),
        ("user name", "TS_IDENTIFIER_INVALID"),
        ("class", "TS_IDENTIFIER_RESERVED"),
        ("interface", "TS_IDENTIFIER_RESERVED"),
        ("éclair", "TS_IDENTIFIER_UNICODE_UNSUPPORTED"),
    ],
)
def test_invalid_candidates(value: str, code: str) -> None:
    diagnostics = TypeScriptTargetAdapter().validate_identifier(
        IdentifierValidationRequest(value, IdentifierRole.VALUE)
    )
    assert code in {item.code for item in diagnostics}


def test_dollar_and_underscore_are_valid() -> None:
    adapter = TypeScriptTargetAdapter()
    for value in ("$user", "_user"):
        diagnostics = adapter.validate_identifier(
            IdentifierValidationRequest(value, IdentifierRole.VALUE)
        )
        assert not diagnostics.has_errors


def test_spec_validated_unicode_subset() -> None:
    adapter = TypeScriptTargetAdapter(
        TypeScriptTargetOptions(unicode_identifier_policy=UnicodeIdentifierPolicy.SPEC_VALIDATED)
    )
    diagnostics = adapter.validate_identifier(
        IdentifierValidationRequest("Éclair", IdentifierRole.TYPE)
    )
    assert not diagnostics.has_errors


def test_diagnostics_are_deterministic() -> None:
    request = IdentifierValidationRequest("1 user", IdentifierRole.PARAMETER)
    adapter = TypeScriptTargetAdapter()
    assert adapter.validate_identifier(request) == adapter.validate_identifier(request)
