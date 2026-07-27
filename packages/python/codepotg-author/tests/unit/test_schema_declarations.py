from enum import StrEnum

from codepotg_author import (
    Author,
    FieldOptions,
    ProjectionStep,
    SchemaDeclaration,
    SchemaDeclarationKind,
    field,
)


class Status(StrEnum):
    ACTIVE = "active"
    DISABLED = "disabled"


def test_property_and_object_schema_are_structural() -> None:
    author = Author("Example")
    email = author.property(
        "Email",
        str,
        options=FieldOptions(format="email", min_length=3),
    )
    user = author.schema(
        "User",
        {
            "id": field(int, readonly=True),
            "email": email,
            "display_name": field(str, required=False, max_length=100),
        },
    )
    payload = author.declaration(user).payload
    assert isinstance(payload, SchemaDeclaration)
    assert payload.kind is SchemaDeclarationKind.OBJECT
    assert [item.name for item in payload.fields] == ["id", "email", "display_name"]
    assert payload.fields[1].property_ref == email


def test_enum_and_projection_are_deterministic() -> None:
    author = Author("Example")
    status = author.enum_schema("Status", Status)
    user = author.schema("User", {"id": int, "status": status, "name": str})
    read = author.project_schema(user, "UserRead", ProjectionStep("pick", ("id", "name")))
    enum_payload = author.declaration(status).payload
    projection = author.declaration(read).payload
    assert isinstance(enum_payload, SchemaDeclaration)
    assert enum_payload.enum_values == ("active", "disabled")
    assert isinstance(projection, SchemaDeclaration)
    assert projection.source_schema == user
    assert projection.projection_steps[0].fields == ("id", "name")


def test_foreign_projection_ref_is_rejected() -> None:
    left = Author("Left")
    right = Author("Right")
    foreign = right.schema("User")
    try:
        left.project_schema(foreign, "Read", ProjectionStep("partial"))
    except ValueError as exc:
        assert str(exc) == "foreign author-session ref"
    else:
        raise AssertionError("foreign ref was accepted")
