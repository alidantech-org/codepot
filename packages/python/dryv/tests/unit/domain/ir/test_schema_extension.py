from dryv.ir import Name, Schema, SchemaField, SchemaKind, SemanticId, TypeExpression
from dryv.ir.schemas import SchemaResolutionError, resolve_effective_schema


def _field(value: str, name: str, kind: str = "string") -> SchemaField:
    return SchemaField(SemanticId(value), Name(name), TypeExpression.primitive(kind))


def test_transitive_schema_extension_merges_fields_in_stable_order() -> None:
    base = Schema(SemanticId("schema.base"), Name("Base"), SchemaKind.OBJECT, fields=(_field("field.id", "id"),))
    middle = Schema(SemanticId("schema.middle"), Name("Middle"), SchemaKind.OBJECT, fields=(_field("field.name", "name"),), extends=base.id)
    leaf = Schema(SemanticId("schema.leaf"), Name("Leaf"), SchemaKind.OBJECT, fields=(_field("field.email", "email"),), extends=middle.id)
    schemas = {item.id: item for item in (base, middle, leaf)}
    effective = resolve_effective_schema(leaf.id, schemas)
    assert effective.lineage == (base.id, middle.id, leaf.id)
    assert tuple(str(item.name) for item in effective.fields) == ("id", "name", "email")


def test_child_field_overrides_same_name_without_reordering() -> None:
    original = _field("field.base.name", "name")
    override = _field("field.child.name", "name")
    base = Schema(SemanticId("schema.base"), Name("Base"), SchemaKind.OBJECT, fields=(original,))
    child = Schema(SemanticId("schema.child"), Name("Child"), SchemaKind.OBJECT, fields=(override,), extends=base.id)
    effective = resolve_effective_schema(child.id, {base.id: base, child.id: child})
    assert effective.fields == (override,)


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
    base = Schema(SemanticId("schema.base"), Name("Base"), SchemaKind.OBJECT, fields=(_field("field.base", "value", "string"),))
    child = Schema(SemanticId("schema.child"), Name("Child"), SchemaKind.OBJECT, fields=(_field("field.child", "value", "integer"),), extends=base.id)
    try:
        resolve_effective_schema(child.id, {base.id: base, child.id: child})
    except SchemaResolutionError as exc:
        assert exc.code == "IR_INCOMPATIBLE_FIELD_OVERRIDE"
    else:
        raise AssertionError("incompatible override must fail")
