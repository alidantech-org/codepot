from dryv.ir import Name, Schema, SchemaField, SchemaKind, SemanticId, TypeExpression
from dryv.ir.schemas import SchemaResolutionError, resolve_effective_schema


def _field(value: str, name: str, kind: str = "string", *, overrides: SemanticId | None = None) -> SchemaField:
    return SchemaField(SemanticId(value), Name(name), TypeExpression.primitive(kind), overrides=overrides)


def test_transitive_schema_extension_merges_fields_in_stable_order_and_preserves_origin() -> None:
    base = Schema(SemanticId("schema.base"), Name("Base"), SchemaKind.OBJECT, fields=(_field("field.id", "id"),))
    middle = Schema(SemanticId("schema.middle"), Name("Middle"), SchemaKind.OBJECT, fields=(_field("field.name", "name"),), extends=base.id)
    leaf = Schema(SemanticId("schema.leaf"), Name("Leaf"), SchemaKind.OBJECT, fields=(_field("field.email", "email"),), extends=middle.id)
    schemas = {item.id: item for item in (base, middle, leaf)}
    effective = resolve_effective_schema(leaf.id, schemas)
    assert effective.lineage == (base.id, middle.id, leaf.id)
    assert tuple(str(item.name) for item in effective.fields) == ("id", "name", "email")
    assert effective.declared_by(SemanticId("field.id")) == base.id
    assert effective.declared_by(SemanticId("field.name")) == middle.id
    assert effective.declared_by(SemanticId("field.email")) == leaf.id


def test_child_field_override_is_explicit_and_does_not_reorder() -> None:
    original = _field("field.base.name", "name")
    override = _field("field.child.name", "name", overrides=original.id)
    base = Schema(SemanticId("schema.base"), Name("Base"), SchemaKind.OBJECT, fields=(original,))
    child = Schema(SemanticId("schema.child"), Name("Child"), SchemaKind.OBJECT, fields=(override,), extends=base.id)
    effective = resolve_effective_schema(child.id, {base.id: base, child.id: child})
    assert effective.fields == (override,)
    assert effective.declared_by(override.id) == child.id


def test_implicit_override_is_rejected() -> None:
    original = _field("field.base.name", "name")
    implicit = _field("field.child.name", "name")
    base = Schema(SemanticId("schema.base"), Name("Base"), SchemaKind.OBJECT, fields=(original,))
    child = Schema(SemanticId("schema.child"), Name("Child"), SchemaKind.OBJECT, fields=(implicit,), extends=base.id)
    try:
        resolve_effective_schema(child.id, {base.id: base, child.id: child})
    except SchemaResolutionError as exc:
        assert exc.code == "IR_IMPLICIT_FIELD_OVERRIDE"
    else:
        raise AssertionError("implicit override must fail")


def test_missing_base_and_cycles_are_explicit_resolution_errors() -> None:
    missing = Schema(SemanticId("schema.missing-child"), Name("MissingChild"), SchemaKind.OBJECT, extends=SemanticId("schema.nope"))
    try:
        resolve_effective_schema(missing.id, {missing.id: missing})
    except SchemaResolutionError as exc:
        assert exc.code == "IR_MISSING_BASE_SCHEMA"
    else:
        raise AssertionError("missing base must fail")

    a = Schema(SemanticId("schema.a"), Name("A"), SchemaKind.OBJECT, extends=SemanticId("schema.b"))
    b = Schema(SemanticId("schema.b"), Name("B"), SchemaKind.OBJECT, extends=a.id)
    try:
        resolve_effective_schema(a.id, {a.id: a, b.id: b})
    except SchemaResolutionError as exc:
        assert exc.code == "IR_SCHEMA_EXTENSION_CYCLE"
    else:
        raise AssertionError("extension cycle must fail")


def test_incompatible_override_type_is_rejected() -> None:
    original = _field("field.base", "value", "string")
    base = Schema(SemanticId("schema.base"), Name("Base"), SchemaKind.OBJECT, fields=(original,))
    child = Schema(SemanticId("schema.child"), Name("Child"), SchemaKind.OBJECT, fields=(_field("field.child", "value", "integer", overrides=original.id),), extends=base.id)
    try:
        resolve_effective_schema(child.id, {base.id: base, child.id: child})
    except SchemaResolutionError as exc:
        assert exc.code == "IR_INCOMPATIBLE_FIELD_OVERRIDE"
    else:
        raise AssertionError("incompatible override must fail")


def test_multiple_direct_bases_are_not_a_valid_schema_reference() -> None:
    try:
        Schema(SemanticId("schema.child"), Name("Child"), SchemaKind.OBJECT, extends=(SemanticId("schema.a"), SemanticId("schema.b")))  # type: ignore[arg-type]
    except ValueError as exc:
        assert "exactly one" in str(exc)
    else:
        raise AssertionError("multiple direct bases must fail")
