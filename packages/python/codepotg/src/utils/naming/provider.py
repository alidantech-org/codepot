"""Unified naming provider for code generation contexts."""

from __future__ import annotations

from dataclasses import dataclass

from utils.naming.aliases import CASE_ALIAS_TO_FIELD
from utils.naming.cases import (
    camel_case,
    clean_name,
    constant_case,
    dot_case,
    kebab_case,
    lower_case,
    pascal_case,
    path_case,
    screaming_case,
    snake_case,
    split_words,
    upper_case,
)
from utils.naming.number import NumberKind
from utils.naming.plurality import categorize_word


@dataclass(frozen=True)
class PluralizedName:
    """A case-specific name with original, stable singular, and plural variants."""

    original: str
    singular: str
    plural: str
    number: NumberKind

    @property
    def o(self) -> str:
        return self.original

    @property
    def s(self) -> str:
        return self.singular

    @property
    def p(self) -> str:
        return self.plural

    def __str__(self) -> str:
        return self.original


@dataclass(frozen=True)
class NameSet:
    """All supported casing variants for one source name."""

    raw: PluralizedName
    clean: PluralizedName
    snake: PluralizedName
    kebab: PluralizedName
    camel: PluralizedName
    pascal: PluralizedName
    screaming: PluralizedName
    constant: PluralizedName
    dot: PluralizedName
    path: PluralizedName
    lower: PluralizedName
    upper: PluralizedName

    def __getattr__(self, key: str) -> PluralizedName:
        field = CASE_ALIAS_TO_FIELD.get(key)
        if field:
            return getattr(self, field)
        raise AttributeError(key)

    @property
    def sn(self) -> PluralizedName:
        """snake alias."""
        return self.snake

    @property
    def kb(self) -> PluralizedName:
        """kebab alias."""
        return self.kebab

    @property
    def cm(self) -> PluralizedName:
        """camel alias."""
        return self.camel

    @property
    def pc(self) -> PluralizedName:
        """pascal alias."""
        return self.pascal

    @property
    def ss(self) -> PluralizedName:
        """screaming alias."""
        return self.screaming

    @property
    def cn(self) -> PluralizedName:
        """constant alias."""
        return self.constant

    @property
    def dt(self) -> PluralizedName:
        """dot alias."""
        return self.dot

    @property
    def pt(self) -> PluralizedName:
        """path alias."""
        return self.path


class NameProvider:
    """Build case-first, pluralization-second name objects.

    Singular forms intentionally preserve the input instead of singularizing a
    plural source token. This avoids collisions such as page/pages both becoming
    page in generated fields.
    """

    def build(self, value: str) -> NameSet:
        original_words = split_words(value)
        forms = self._categorize_words(original_words)

        original = " ".join(forms["original"])
        singular = " ".join(forms["singular"])
        plural = " ".join(forms["plural"])
        number = forms["number"]

        return NameSet(
            raw=PluralizedName(value.strip(), singular, plural, number),
            clean=self._case(original, singular, plural, number, clean_name),
            snake=self._case(original, singular, plural, number, snake_case),
            kebab=self._case(original, singular, plural, number, kebab_case),
            camel=self._case(original, singular, plural, number, camel_case),
            pascal=self._case(original, singular, plural, number, pascal_case),
            screaming=self._case(original, singular, plural, number, screaming_case),
            constant=self._case(original, singular, plural, number, constant_case),
            dot=self._case(original, singular, plural, number, dot_case),
            path=self._case(original, singular, plural, number, path_case),
            lower=self._case(original, singular, plural, number, lower_case),
            upper=self._case(original, singular, plural, number, upper_case),
        )

    def _categorize_words(self, words: list[str]) -> dict[str, list[str] | NumberKind]:
        if not words:
            return {
                "original": [],
                "singular": [],
                "plural": [],
                "number": NumberKind.UNKNOWN,
            }

        original = list(words)
        singular = list(words)
        plural = list(words)

        last = categorize_word(words[-1])
        plural[-1] = last.plural

        return {
            "original": original,
            "singular": singular,
            "plural": plural,
            "number": last.kind,
        }

    def _case(
        self,
        original: str,
        singular: str,
        plural: str,
        number: NumberKind,
        converter,
    ) -> PluralizedName:
        return PluralizedName(
            original=converter(original),
            singular=converter(singular),
            plural=converter(plural),
            number=number,
        )


def build_name(value: str) -> NameSet:
    """Convenience helper for one-off name creation."""
    return NameProvider().build(value)
