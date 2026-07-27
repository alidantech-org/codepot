from __future__ import annotations

import pytest

from codepotg_openapi.references.pointer import (
    JsonPointerError,
    normalize_fragment,
    resolve_pointer,
)


def test_decodes_json_pointer_escapes() -> None:
    value = {"a/b": {"~key": 42}}
    assert resolve_pointer(value, "/a~1b/~0key") == 42


def test_normalizes_percent_encoded_fragment() -> None:
    assert normalize_fragment("/a%20b") == "/a b"


@pytest.mark.parametrize("pointer", ["value", "/bad~2escape", "/bad~"])
def test_rejects_malformed_pointer(pointer: str) -> None:
    with pytest.raises(JsonPointerError):
        resolve_pointer({}, pointer)


def test_array_pointer_bounds() -> None:
    assert resolve_pointer(["a", "b"], "/1") == "b"
    with pytest.raises(JsonPointerError):
        resolve_pointer(["a"], "/2")
