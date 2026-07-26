from __future__ import annotations

import re
from dataclasses import dataclass, field
from functools import cached_property
from typing import Callable

_WORD_BOUNDARY_1 = re.compile(r"([a-z0-9])([A-Z])")
_WORD_BOUNDARY_2 = re.compile(r"([A-Z]+)([A-Z][a-z])")
_NON_WORD = re.compile(r"[^A-Za-z0-9]+")

_UNCOUNTABLE = {
    "advice",
    "data",
    "equipment",
    "fish",
    "information",
    "money",
    "news",
    "rice",
    "series",
    "sheep",
    "species",
}

_IRREGULAR_PLURAL = {
    "child": "children",
    "foot": "feet",
    "goose": "geese",
    "man": "men",
    "mouse": "mice",
    "person": "people",
    "tooth": "teeth",
    "woman": "women",
}
_IRREGULAR_SINGULAR = {plural: singular for singular, plural in _IRREGULAR_PLURAL.items()}


@dataclass(frozen=True, slots=True)
class NameProjection:
    original: str
    singular: str
    plural: str

    @property
    def o(self) -> str:
        return self.original

    @property
    def s(self) -> str:
        return self.singular

    @property
    def p(self) -> str:
        return self.plural


@dataclass(frozen=True)
class Name:
    value: str
    _tokens: tuple[str, ...] = field(init=False, repr=False)

    def __post_init__(self) -> None:
        if not self.value or self.value.strip() != self.value:
            raise ValueError("semantic names must be non-empty trimmed strings")
        tokens = _split_words(self.value)
        if not tokens:
            raise ValueError(f"semantic name contains no usable characters: {self.value!r}")
        object.__setattr__(self, "_tokens", tokens)

    @cached_property
    def raw(self) -> NameProjection:
        return NameProjection(
            original=self.value,
            singular=_join_original(_singularize_tokens(self._tokens)),
            plural=_join_original(_pluralize_tokens(self._tokens)),
        )

    @cached_property
    def clean(self) -> NameProjection:
        return self._project(lambda tokens: " ".join(tokens))

    @cached_property
    def snake(self) -> NameProjection:
        return self._project(lambda tokens: "_".join(tokens))

    @cached_property
    def kebab(self) -> NameProjection:
        return self._project(lambda tokens: "-".join(tokens))

    @cached_property
    def camel(self) -> NameProjection:
        return self._project(_camel)

    @cached_property
    def pascal(self) -> NameProjection:
        return self._project(_pascal)

    @cached_property
    def screaming(self) -> NameProjection:
        return self._project(lambda tokens: "_".join(tokens).upper())

    @cached_property
    def constant(self) -> NameProjection:
        return self.screaming

    @cached_property
    def dot(self) -> NameProjection:
        return self._project(lambda tokens: ".".join(tokens))

    @cached_property
    def path(self) -> NameProjection:
        return self._project(lambda tokens: "/".join(tokens))

    @cached_property
    def lower(self) -> NameProjection:
        return self._project(lambda tokens: "".join(tokens).lower())

    @cached_property
    def upper(self) -> NameProjection:
        return self._project(lambda tokens: "".join(tokens).upper())

    def _project(self, transform: Callable[[tuple[str, ...]], str]) -> NameProjection:
        return NameProjection(
            original=transform(self._tokens),
            singular=transform(_singularize_tokens(self._tokens)),
            plural=transform(_pluralize_tokens(self._tokens)),
        )


def pluralize(word: str) -> str:
    if not word:
        raise ValueError("cannot pluralize an empty word")
    lower = word.lower()
    if lower in _UNCOUNTABLE:
        return word
    if lower in _IRREGULAR_PLURAL:
        return _match_case(word, _IRREGULAR_PLURAL[lower])
    if lower.endswith("y") and len(lower) > 1 and lower[-2] not in "aeiou":
        return word[:-1] + _match_case(word[-1], "ies")
    if lower.endswith(("s", "x", "z", "ch", "sh")):
        return word + _match_case(word[-1], "es")
    if lower.endswith("fe"):
        return word[:-2] + _match_case(word[-2:], "ves")
    if lower.endswith("f"):
        return word[:-1] + _match_case(word[-1], "ves")
    return word + _match_case(word[-1], "s")


def singularize(word: str) -> str:
    if not word:
        raise ValueError("cannot singularize an empty word")
    lower = word.lower()
    if lower in _UNCOUNTABLE:
        return word
    if lower in _IRREGULAR_SINGULAR:
        return _match_case(word, _IRREGULAR_SINGULAR[lower])
    if lower.endswith("ies") and len(lower) > 3:
        return word[:-3] + _match_case(word[-3:], "y")
    if lower.endswith("ves") and len(lower) > 3:
        base = word[:-3]
        return base + _match_case(word[-3:], "f")
    if lower.endswith(("ches", "shes", "xes", "zes", "sses")):
        return word[:-2]
    if lower.endswith("s") and not lower.endswith("ss"):
        return word[:-1]
    return word


def _split_words(value: str) -> tuple[str, ...]:
    value = _WORD_BOUNDARY_2.sub(r"\1 \2", value)
    value = _WORD_BOUNDARY_1.sub(r"\1 \2", value)
    return tuple(part.lower() for part in _NON_WORD.sub(" ", value).split() if part)


def _pluralize_tokens(tokens: tuple[str, ...]) -> tuple[str, ...]:
    return tokens[:-1] + (pluralize(tokens[-1]),)


def _singularize_tokens(tokens: tuple[str, ...]) -> tuple[str, ...]:
    return tokens[:-1] + (singularize(tokens[-1]),)


def _camel(tokens: tuple[str, ...]) -> str:
    first, *rest = tokens
    return first + "".join(token[:1].upper() + token[1:] for token in rest)


def _pascal(tokens: tuple[str, ...]) -> str:
    return "".join(token[:1].upper() + token[1:] for token in tokens)


def _join_original(tokens: tuple[str, ...]) -> str:
    return " ".join(tokens)


def _match_case(source: str, replacement: str) -> str:
    if source.isupper():
        return replacement.upper()
    if source[:1].isupper():
        return replacement[:1].upper() + replacement[1:]
    return replacement
