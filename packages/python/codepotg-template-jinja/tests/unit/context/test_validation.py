from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

import pytest

from codepotg.ir import Name, SchemaKind, SemanticId
from codepotg_template_jinja import JinjaEngineRules
from codepotg_template_jinja.context import ContextSafetyError, SafeRecord, freeze_context


def test_freezes_scalars_sequences_and_sorted_pair_mappings() -> None:
    frozen = freeze_context(
        (
            ("items", (1, "two", False, None)),
            ("meta", (("enabled", True), ("name", "demo"))),
        ),
        JinjaEngineRules(),
    )
    assert isinstance(frozen, SafeRecord)
    assert frozen["items"] == (1, "two", False, None)
    assert frozen["meta"]["name"] == "demo"  # type: ignore[index]


def test_name_projections_are_preserved_without_mutating_original() -> None:
    name = Name("order item")
    before = dict(vars(name))
    frozen = freeze_context((("name", name),), JinjaEngineRules())
    assert frozen["name"]["pascal"]["s"] == "OrderItem"  # type: ignore[index]
    assert frozen["name"]["snake"]["p"] == "order_items"  # type: ignore[index]
    assert vars(name) == before


def test_public_semantic_id_and_enum_are_supported() -> None:
    frozen = freeze_context(
        (("id", SemanticId("group:orders")), ("kind", SchemaKind.OBJECT)),
        JinjaEngineRules(),
    )
    assert frozen["id"]["value"] == "group:orders"  # type: ignore[index]
    assert frozen["kind"] == "object"


class UserEnum(StrEnum):
    VALUE = "value"


def test_arbitrary_user_enums_are_rejected() -> None:
    with pytest.raises(ContextSafetyError) as captured:
        freeze_context((("value", UserEnum.VALUE),), JinjaEngineRules())
    assert captured.value.code == "JINJA_CONTEXT_UNSAFE"


@dataclass(frozen=True)
class UserRecord:
    value: str


def test_arbitrary_dataclasses_are_rejected() -> None:
    with pytest.raises(ContextSafetyError) as captured:
        freeze_context((("record", UserRecord("x")),), JinjaEngineRules())
    assert captured.value.code == "JINJA_CONTEXT_UNSAFE"


@pytest.mark.parametrize("value", [lambda: None, print, UserRecord])
def test_callables_and_classes_are_rejected(value: object) -> None:
    with pytest.raises(ContextSafetyError) as captured:
        freeze_context((("value", value),), JinjaEngineRules())
    assert captured.value.code in {"JINJA_CALLABLE_DENIED", "JINJA_CONTEXT_UNSAFE"}


@pytest.mark.parametrize("key", ["_private", "not-valid", "", "1value"])
def test_context_keys_are_restricted(key: str) -> None:
    with pytest.raises(ContextSafetyError):
        freeze_context(((key, "value"),), JinjaEngineRules())


def test_nested_mapping_keys_must_be_sorted_unique() -> None:
    with pytest.raises(ContextSafetyError, match="sorted"):
        freeze_context((("value", (("b", 1), ("a", 2))),), JinjaEngineRules())


def test_context_depth_limit_is_enforced() -> None:
    rules = JinjaEngineRules(max_context_depth=2)
    with pytest.raises(ContextSafetyError) as captured:
        freeze_context((("value", (((1,),),)),), rules)
    assert captured.value.code == "JINJA_CONTEXT_LIMIT"


def test_context_item_limit_is_enforced() -> None:
    rules = JinjaEngineRules(max_context_items=2)
    with pytest.raises(ContextSafetyError) as captured:
        freeze_context((("value", (1, 2)),), rules)
    assert captured.value.code == "JINJA_CONTEXT_LIMIT"


@pytest.mark.parametrize("value", [float("inf"), float("-inf"), float("nan")])
def test_non_finite_floats_are_rejected(value: float) -> None:
    with pytest.raises(ContextSafetyError):
        freeze_context((("value", value),), JinjaEngineRules())
