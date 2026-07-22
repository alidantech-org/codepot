"""Shared naming utilities for generator contexts.

The naming package exposes a unified NameProvider used by language planners,
emission planners, template path expansion, and debug rendering. Access order
is case-first and pluralisation-second, for example name.snake.s or name.path.p.
Singular access is stable and preserves the authored name; use plural access
only where a generated plural form is explicitly required.
"""

from utils.naming.provider import NameProvider, NameSet, PluralizedName, build_name

__all__ = [
    "NameProvider",
    "NameSet",
    "PluralizedName",
    "build_name",
]
