from __future__ import annotations

import pytest

from codepotg_template_jinja.helpers.builtins import (
    filter_indent,
    filter_join,
    filter_replace,
    filter_sort,
    filter_unique,
)


def test_join_accepts_only_immutable_tuples() -> None:
    assert filter_join(("a", "b"), ",") == "a,b"
    with pytest.raises(TypeError):
        filter_join(["a", "b"], ",")


def test_replace_validates_count() -> None:
    assert filter_replace("aaaa", "a", "b", 2) == "bbaa"
    with pytest.raises(TypeError):
        filter_replace("a", "a", "b", -1)


def test_indent_is_deterministic() -> None:
    assert filter_indent("a\n\nb\n", 2) == "a\n\n  b\n"
    assert filter_indent("a\nb", "--", first=True) == "--a\n--b"


def test_sort_requires_homogeneous_scalars() -> None:
    assert filter_sort((3, 1, 2)) == (1, 2, 3)
    with pytest.raises(TypeError):
        filter_sort((1, "2"))


def test_unique_preserves_first_occurrence_order() -> None:
    assert filter_unique(("b", "a", "b", "c")) == ("b", "a", "c")
