from dryv_author import Author, RefKind


def test_sessions_are_isolated_and_refs_are_kind_specific() -> None:
    left = Author("Left")
    right = Author("Right")
    left_schema = left.schema("User")
    right_schema = right.schema("User")
    assert left_schema.kind is RefKind.SCHEMA
    assert left_schema.identity.author_id != right_schema.identity.author_id
    assert left_schema != right_schema


def test_freeze_rejects_late_declarations() -> None:
    author = Author("Example")
    author.schema("User")
    author.freeze()
    try:
        author.schema("Order")
    except RuntimeError as exc:
        assert str(exc) == "author session is frozen"
    else:
        raise AssertionError("late declaration was accepted")


def test_ref_usage_is_immutable() -> None:
    schema = Author("Example").schema("User")
    usage = schema.optional().nullable_value().array_value()
    assert usage.required is False
    assert usage.nullable is True
    assert usage.array is True
    assert schema.kind is RefKind.SCHEMA
