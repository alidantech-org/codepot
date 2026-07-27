from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from codepotg_template_jinja import JinjaEngineRules


def test_rules_use_strict_safe_defaults() -> None:
    rules = JinjaEngineRules()
    assert rules.trim_blocks is True
    assert rules.lstrip_blocks is True
    assert rules.keep_trailing_newline is True
    assert rules.newline_sequence == "\n"
    assert rules.max_render_bytes == 5_000_000
    assert rules.cache_entries == 256


@pytest.mark.parametrize(
    "field,value",
    [
        ("max_template_bytes", 0),
        ("max_partial_count", -1),
        ("max_context_depth", True),
        ("max_render_bytes", 1.5),
        ("cache_entries", "2"),
    ],
)
def test_positive_integer_rules_are_validated(field: str, value: object) -> None:
    with pytest.raises(ValueError, match=field):
        JinjaEngineRules(**{field: value})


@pytest.mark.parametrize("newline", ["x", "\n\r", ""])
def test_newline_sequence_is_validated(newline: str) -> None:
    with pytest.raises(ValueError, match="newline_sequence"):
        JinjaEngineRules(newline_sequence=newline)


def test_rules_are_frozen() -> None:
    rules = JinjaEngineRules()
    with pytest.raises(FrozenInstanceError):
        rules.max_render_bytes = 10  # type: ignore[misc]


def test_rule_identity_is_stable_and_field_ordered() -> None:
    first = JinjaEngineRules().identity()
    second = JinjaEngineRules().identity()
    assert first == second
    assert tuple(name for name, _ in first) == (
        "trim_blocks",
        "lstrip_blocks",
        "keep_trailing_newline",
        "newline_sequence",
        "max_template_id_length",
        "max_template_bytes",
        "max_partial_count",
        "max_partial_bytes",
        "max_context_depth",
        "max_context_items",
        "max_include_depth",
        "max_render_bytes",
        "max_ast_nodes",
        "cache_entries",
    )
