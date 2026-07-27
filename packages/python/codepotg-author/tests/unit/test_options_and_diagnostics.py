from codepotg_author import AuthorDiagnostic, AuthorDiagnostics, AuthorOptions


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
            AuthorDiagnostic("AUTHOR_REF_MISSING", "missing", declaration_path="z"),
            AuthorDiagnostic("AUTHOR_DUPLICATE_ID", "duplicate", declaration_path="a"),
        ]
    )
    assert [item.code for item in values] == ["AUTHOR_DUPLICATE_ID", "AUTHOR_REF_MISSING"]
