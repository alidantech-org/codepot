from __future__ import annotations

import pytest

from dryv.features.hashing import (
    HashingError,
    HashPurpose,
    hash_branch,
    hash_build_inputs,
    hash_bytes,
    hash_value,
)


def test_canonical_values_ignore_object_key_order() -> None:
    first = hash_value(HashPurpose.CANONICAL_DOCUMENT, {"b": 2, "a": [1, True]})
    second = hash_value(HashPurpose.CANONICAL_DOCUMENT, {"a": [1, True], "b": 2})
    assert first == second
    assert first.identity.startswith("sha256:v1:canonical-document:")


def test_hash_purpose_is_part_of_identity() -> None:
    content = b"same"
    resource = hash_bytes(HashPurpose.RESOURCE_CONTENT, content)
    template = hash_bytes(HashPurpose.TEMPLATE_CONTENT, content)
    assert resource.digest == template.digest
    assert resource.identity != template.identity


def test_branch_hash_changes_only_for_reachable_dependencies() -> None:
    direct = {
        "root": hash_bytes(HashPurpose.IR_RECORD, b"root"),
        "child": hash_bytes(HashPurpose.IR_RECORD, b"child"),
        "unrelated": hash_bytes(HashPurpose.IR_RECORD, b"one"),
    }
    dependencies = {"root": ("child",), "child": (), "unrelated": ()}
    first = hash_branch("root", direct, dependencies)

    changed = dict(direct)
    changed["unrelated"] = hash_bytes(HashPurpose.IR_RECORD, b"two")
    assert hash_branch("root", changed, dependencies) == first

    changed["child"] = hash_bytes(HashPurpose.IR_RECORD, b"changed")
    assert hash_branch("root", changed, dependencies) != first


def test_branch_cycles_are_structured_errors() -> None:
    direct = {
        "a": hash_bytes(HashPurpose.IR_RECORD, b"a"),
        "b": hash_bytes(HashPurpose.IR_RECORD, b"b"),
    }
    with pytest.raises(HashingError) as caught:
        hash_branch("a", direct, {"a": ("b",), "b": ("a",)})
    assert caught.value.code == "HASH_DEPENDENCY_CYCLE"


def test_build_input_hash_is_order_independent() -> None:
    a = hash_bytes(HashPurpose.CONTEXT, b"a")
    b = hash_bytes(HashPurpose.TEMPLATE_CONTENT, b"b")
    assert hash_build_inputs({"a": a, "b": b}) == hash_build_inputs({"b": b, "a": a})
