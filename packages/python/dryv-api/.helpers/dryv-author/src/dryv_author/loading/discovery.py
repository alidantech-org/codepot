from __future__ import annotations

from pathlib import Path

from dryv_author.api import Author

from .module import load_module
from .target import AuthorTarget


def discover_author(target: str | AuthorTarget, *, project_root: Path | None = None) -> Author:
    parsed = AuthorTarget.parse(target) if isinstance(target, str) else target
    module = load_module(parsed, project_root=project_root)
    if parsed.attribute:
        if not hasattr(module, parsed.attribute):
            raise ValueError(f"author module {parsed.location!r} has no attribute {parsed.attribute!r}")
        return _materialize(getattr(module, parsed.attribute), parsed.attribute)
    for name in ("AUTHOR", "build_author", "author"):
        if hasattr(module, name):
            return _materialize(getattr(module, name), name)
    raise ValueError("author module must expose AUTHOR, build_author(), author(), or an explicit :attribute")


def _materialize(value: object, label: str) -> Author:
    result = value() if callable(value) and not isinstance(value, Author) else value
    if not isinstance(result, Author):
        raise TypeError(f"author entry {label!r} did not produce dryv_author.Author")
    return result


__all__ = ["discover_author"]
