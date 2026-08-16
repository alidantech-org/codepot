from dryv_author import (
    AUTHOR_CORE_UNSUPPORTED,
    Author,
    AuthorDiagnostic,
    AuthorDiagnostics,
    AuthorDiagnosticSeverity,
    AuthorOptions,
    RefKind,
)


def test_options_reject_unknown_fields() -> None:
    try:
        AuthorOptions.from_mapping({"framework": "fastapi"})
    except ValueError as exc:
        assert "unknown author options" in str(exc)
    else:
        raise AssertionError("unknown option was accepted")


def test_diagnostics_are_stably_sorted() -> None:
    values = AuthorDiagnostics.from_iterable(
        [
            AuthorDiagnostic(
                code="AUTHOR_REF_MISSING",
                severity=AuthorDiagnosticSeverity.ERROR,
                message="missing",
            ),
            AuthorDiagnostic(
                code="AUTHOR_DUPLICATE_ID",
                severity=AuthorDiagnosticSeverity.ERROR,
                message="duplicate",
            ),
        ]
    )
    assert [item.code for item in values] == ["AUTHOR_DUPLICATE_ID", "AUTHOR_REF_MISSING"]


def test_unsupported_core_kind_is_diagnostic_and_not_collected() -> None:
    author = Author("example")

    try:
        author.declare(RefKind.VALUE_SOURCE, "request-user")
    except ValueError as exc:
        assert str(exc).startswith(AUTHOR_CORE_UNSUPPORTED)
    else:
        raise AssertionError("unsupported core kind was accepted")

    assert author.declarations == ()
    assert [item.code for item in author.diagnostics] == [AUTHOR_CORE_UNSUPPORTED]
