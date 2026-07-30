from __future__ import annotations

from dataclasses import dataclass

import pytest

from contracts.normalized import (
    ContractReference,
    DiagnosticCategory,
    DiagnosticLevel,
    PresenceValue,
    ReferenceKind,
    ResolutionState,
    SchemaUse,
    SchemaUseKind,
    ValueOrigin,
    contract_collection,
    presence_from_mapping,
    source_object,
    structured_notes,
)


def test_presence_value_distinguishes_missing_null_false_zero_and_empty() -> None:
    source = {
        "null": None,
        "false": False,
        "zero": 0,
        "empty_string": "",
        "empty_list": [],
    }

    missing = presence_from_mapping(source, "missing", source_path="schema")
    explicit_null = presence_from_mapping(source, "null", source_path="schema")
    explicit_false = presence_from_mapping(source, "false", source_path="schema")
    explicit_zero = presence_from_mapping(source, "zero", source_path="schema")
    explicit_string = presence_from_mapping(source, "empty_string", source_path="schema")
    explicit_list = presence_from_mapping(source, "empty_list", source_path="schema")

    assert not missing.is_set
    assert missing.origin == ValueOrigin.MISSING
    assert missing.source_path == "schema.missing"

    assert explicit_null.is_set
    assert explicit_null.is_null
    assert explicit_null.is_authored
    assert explicit_null.value is None

    assert explicit_false.value is False
    assert explicit_zero.value == 0
    assert explicit_string.value == ""
    assert explicit_list.value == ()


def test_presence_value_origin_helpers_are_stable() -> None:
    inferred = PresenceValue.inferred("value", source_path="x")
    derived = PresenceValue.derived("value", source_path="x")
    effective = PresenceValue.effective("value", source_path="x")

    assert inferred.is_inferred and not inferred.is_authored
    assert derived.is_derived and not derived.is_effective
    assert effective.is_effective and effective.origin == ValueOrigin.EFFECTIVE


def test_source_object_freezes_raw_extensions_and_diagnoses_raw_only_keys() -> None:
    source = source_object(
        {
            "type": "string",
            "x-project": {"enabled": True},
            "futureKeyword": {"nested": [1, 2]},
        },
        source_path="components.schemas.Identifier",
        known_keys={"type"},
    )

    assert source.raw["type"] == "string"
    assert source.extensions["x-project"]["enabled"] is True
    assert source.raw["futureKeyword"]["nested"] == (1, 2)
    assert source.loss_count == 0
    assert len(source.diagnostics) == 1
    diagnostic = source.diagnostics[0]
    assert diagnostic.category == DiagnosticCategory.RAW_ONLY
    assert diagnostic.level == DiagnosticLevel.INFO
    assert diagnostic.source_path.endswith("futureKeyword")

    with pytest.raises(TypeError):
        source.raw["new"] = "value"  # type: ignore[index]


def test_contract_reference_preserves_ref_and_resolution_state() -> None:
    target = object()
    unresolved = ContractReference(
        ref="#/components/schemas/User",
        kind=ReferenceKind.SCHEMA,
        name="User",
        owner="CreateUserDto",
    )
    resolved = ContractReference(
        ref=unresolved.ref,
        kind=unresolved.kind,
        name=unresolved.name,
        owner=unresolved.owner,
        state=ResolutionState.RESOLVED,
        target=target,
    )

    assert not unresolved.is_resolved
    assert unresolved.ref == resolved.ref
    assert resolved.is_resolved
    assert resolved.target is target


def test_schema_use_supports_inline_reference_and_resolved_forms() -> None:
    reference = ContractReference(
        ref="#/components/schemas/User",
        kind=ReferenceKind.SCHEMA,
    )
    referenced = SchemaUse(kind=SchemaUseKind.REFERENCE, ref=reference, refs=(reference,))
    inline = SchemaUse(
        kind=SchemaUseKind.INLINE,
        inline=source_object({"type": "string"}).raw,
    )
    target = object()
    resolved_ref = ContractReference(
        ref=reference.ref,
        kind=ReferenceKind.SCHEMA,
        state=ResolutionState.RESOLVED,
        target=target,
    )
    resolved = SchemaUse(
        kind=SchemaUseKind.RESOLVED,
        ref=resolved_ref,
        refs=(resolved_ref,),
        schema=target,
    )

    assert referenced.is_reference
    assert not referenced.is_resolved
    assert inline.is_inline
    assert inline.inline["type"] == "string"
    assert not resolved.is_reference
    assert resolved.is_resolved


@dataclass(frozen=True)
class Item:
    id: str
    name: str
    kind: str


def test_contract_collection_is_ordered_classified_and_reports_collisions() -> None:
    items = (
        Item(id="one", name="First", kind="model"),
        Item(id="two", name="Second", kind="dto"),
        Item(id="two", name="Second Again", kind="dto"),
    )

    collection = contract_collection(
        items,
        classifiers={
            "models": lambda item: item.kind == "model",
            "dtos": lambda item: item.kind == "dto",
        },
    )

    assert collection.all == items
    assert collection.count == 3
    assert collection.by_id["one"] is items[0]
    assert collection.by_id["two"] is items[1]
    assert collection.by_name["Second Again"] is items[2]
    assert collection.group("models") == (items[0],)
    assert collection.group("dtos") == (items[1], items[2])
    assert collection.group("missing") == ()
    assert collection.get("one") is items[0]
    assert collection.collisions[0].lookup == "id"
    assert collection.collisions[0].value == "two"
    assert collection.collisions[0].indexes == (1, 2)


def test_structured_notes_preserves_known_and_unknown_categories() -> None:
    notes = structured_notes(
        {
            "explain": "Why this exists",
            "implementation": ["Add cache", "Add retry"],
            "security": "Require auth",
            "business": ["Premium only"],
        }
    )

    assert notes.explain == ("Why this exists",)
    assert notes.implement == ("Add cache", "Add retry")
    assert notes.security == ("Require auth",)
    assert notes.other["business"] == ("Premium only",)
