"""Compatibility facade for the former semantic namespace.

Canonical Dryv IR is owned by :mod:`dryv.ir`. This namespace remains only so
existing consumers can migrate without creating a second semantic model.
"""
from importlib import import_module
from typing import Any

_CANONICAL = import_module("dryv.ir.model")
__all__ = tuple(getattr(_CANONICAL, "__all__", ()))


def __getattr__(name: str) -> Any:
    try:
        return getattr(_CANONICAL, name)
    except AttributeError as exc:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}") from exc


def __dir__() -> list[str]:
    return sorted(set(globals()) | set(__all__))
