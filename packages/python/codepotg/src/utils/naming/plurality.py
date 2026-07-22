"""Pluralisation adapter for generated names.

This module is the only place that imports the third-party pluralizer package.
The rest of the generator consumes categorize_word() only.
"""

from __future__ import annotations

from functools import lru_cache

from utils.naming.number import NumberForms, NumberKind

PROTECTED_WORDS = frozenset(
    {
        "shared",
        "common",
        "base",
        "core",
        "metadata",
        "data",
        "status",
        "settings",
        "config",
        "auth",
        "admin",
        "public",
        "private",
        "internal",
        "system",
        "latest",
        "default",
        "global",
    }
)


@lru_cache(maxsize=1)
def _engine():
    from pluralizer import Pluralizer  # type: ignore

    return Pluralizer()


@lru_cache(maxsize=4096)
def categorize_word(value: str) -> NumberForms:
    """Categorize a word without assuming it is singular or plural."""
    word = value.strip()

    if not word:
        return NumberForms(word, word, word, NumberKind.UNKNOWN)

    if _is_protected(word):
        return NumberForms(word, word, word, NumberKind.INVARIANT)

    singular = _safe_singularize(word)
    plural = _safe_pluralize(singular)

    kind = _detect_number(word, singular, plural)

    if kind is NumberKind.PLURAL:
        return NumberForms(
            original=word,
            singular=_match_style(word, singular),
            plural=word,
            kind=kind,
        )

    if kind is NumberKind.SINGULAR:
        return NumberForms(
            original=word,
            singular=word,
            plural=_match_style(word, plural),
            kind=kind,
        )

    return NumberForms(
        original=word,
        singular=_match_style(word, singular),
        plural=_match_style(word, plural),
        kind=kind,
    )


def _safe_singularize(word: str) -> str:
    if _is_protected(word):
        return word

    result = str(_engine().singular(word))
    return result or word


def _safe_pluralize(word: str) -> str:
    if _is_protected(word):
        return word

    result = str(_engine().plural(word))
    return result or word


def _detect_number(word: str, singular: str, plural: str) -> NumberKind:
    lowered = word.lower()

    if singular.lower() == plural.lower() == lowered:
        return NumberKind.INVARIANT

    if lowered == plural.lower() and lowered != singular.lower():
        return NumberKind.PLURAL

    if lowered == singular.lower():
        return NumberKind.SINGULAR

    return NumberKind.UNKNOWN


def _is_protected(word: str) -> bool:
    return word.lower() in PROTECTED_WORDS


def _match_style(source: str, target: str) -> str:
    if source.isupper():
        return target.upper()

    if source[:1].isupper():
        return target.capitalize()

    return target
