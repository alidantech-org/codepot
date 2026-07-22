"""Unified naming provider for code generation contexts."""

from __future__ import annotations

from archives.codepot.src.contracts.spec.names import SpecName, SpecNameCases
from archives.codepot.src.utils.naming.cases import (
    camel_case,
    clean_name,
    constant_case,
    kebab_case,
    pascal_case,
    path_case,
    screaming_snake_case,
    snake_case,
    split_words,
)
from archives.codepot.src.utils.naming.plurality import categorize_word


def _build_cases(value: str) -> SpecNameCases:
    """Apply all case converters to a single string."""
    return SpecNameCases(
        raw=value,
        clean=clean_name(value),
        pascal=pascal_case(value),
        camel=camel_case(value),
        snake=snake_case(value),
        kebab=kebab_case(value),
        screaming_snake=screaming_snake_case(value),
        constant=constant_case(value),
        path=path_case(value),
    )


class NameProvider:
    """Build SpecName objects from raw string values.

    Access pattern is case-on-the-name, plurality-on-singular/plural:

        name.snake          → snake_case of the original input
        name.singular.snake → snake_case, last word singularised
        name.plural.snake   → snake_case, last word pluralised
    """

    def build(self, value: str) -> SpecName:
        words = split_words(value)
        last_word = words[-1] if words else ""
        last = categorize_word(last_word)

        # Rebuild singular/plural inputs by swapping only the last word,
        # then re-join so case converters see a consistent word list.
        singular_input = " ".join(words[:-1] + [last.singular]) if words else ""
        plural_input = " ".join(words[:-1] + [last.plural]) if words else ""

        return SpecName(
            # Top-level fields: cased forms of the original input.
            raw=value.strip(),
            clean=clean_name(value),
            pascal=pascal_case(value),
            camel=camel_case(value),
            snake=snake_case(value),
            kebab=kebab_case(value),
            screaming_snake=screaming_snake_case(value),
            constant=constant_case(value),
            path=path_case(value),
            # Nested: all case variants of the singularised/pluralised form.
            singular=_build_cases(singular_input),
            plural=_build_cases(plural_input),
        )


def build_name(value: str) -> SpecName:
    """Convenience helper for one-off name building."""
    return NameProvider().build(value)
