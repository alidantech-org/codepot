from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from dryv_template_jinja.helpers import (
    HelperConflictError,
    HelperDescriptor,
    HelperKind,
    HelperRegistry,
)


def identity(value: object) -> object:
    return value


def test_registry_is_sorted_and_has_no_default_globals() -> None:
    registry = HelperRegistry.create()
    assert registry.descriptors == tuple(
        sorted(registry.descriptors, key=lambda item: item.identity())
    )
    assert registry.globals() == {}
    assert "attr" not in registry.filters()
    assert "map" not in registry.filters()
    assert "tojson" not in registry.filters()


def test_custom_helper_version_contributes_to_identity() -> None:
    first = HelperRegistry.create(
        (HelperDescriptor("custom", "custom", HelperKind.FILTER, "1", identity),)
    )
    second = HelperRegistry.create(
        (HelperDescriptor("custom", "custom", HelperKind.FILTER, "2", identity),)
    )
    assert first.identity != second.identity


def test_duplicate_helper_names_are_rejected_across_kinds() -> None:
    custom = HelperDescriptor("custom", "lower", HelperKind.TEST, "1", identity)
    with pytest.raises(HelperConflictError, match="lower"):
        HelperRegistry.create((custom,))


def test_impure_helpers_are_rejected() -> None:
    with pytest.raises(ValueError, match="pure"):
        HelperDescriptor("unsafe", "unsafe", HelperKind.FILTER, "1", identity, pure=False)


def test_descriptors_are_frozen() -> None:
    helper = HelperDescriptor("custom", "custom", HelperKind.FILTER, "1", identity)
    with pytest.raises(FrozenInstanceError):
        helper.version = "2"  # type: ignore[misc]
