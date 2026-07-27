from __future__ import annotations

import pytest

from codepotg.ir import Name, pluralize, singularize


def test_name_contract_uses_case_then_number_order() -> None:
    name = Name("OrderItem")

    assert name.camel.original == "orderItem"
    assert name.camel.singular == "orderItem"
    assert name.camel.plural == "orderItems"
    assert name.camel.o == "orderItem"
    assert name.camel.s == "orderItem"
    assert name.camel.p == "orderItems"
    assert name.pascal.plural == "OrderItems"
    assert name.kebab.plural == "order-items"
    assert name.snake.plural == "order_items"
    assert name.path.plural == "order/items"
    assert name.dot.plural == "order.items"
    assert name.screaming.plural == "ORDER_ITEMS"


def test_names_handle_acronyms_irregulars_and_uncountables() -> None:
    assert Name("HTTPUser").pascal.plural == "HttpUsers"
    assert Name("Person").pascal.plural == "People"
    assert Name("People").pascal.singular == "Person"
    assert Name("Series").snake.plural == "series"
    assert pluralize("category") == "categories"
    assert singularize("categories") == "category"


def test_name_rejects_empty_or_symbol_only_values() -> None:
    with pytest.raises(ValueError):
        Name("")
    with pytest.raises(ValueError):
        Name("---")
