"""Name contracts for normalized spec records."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class SpecNameCase(StrEnum):
    """Supported name case selectors."""

    RAW = "raw"
    CLEAN = "clean"
    PASCAL = "pascal"
    CAMEL = "camel"
    SNAKE = "snake"
    KEBAB = "kebab"
    SCREAMING_SNAKE = "screaming_snake"
    CONSTANT = "constant"
    PATH = "path"


@dataclass(frozen=True)
class SpecNameCases:
    """Prepared casing variants for one name."""

    raw: str
    clean: str
    pascal: str
    camel: str
    snake: str
    kebab: str
    screaming_snake: str
    constant: str
    path: str

    @property
    def rw(self) -> str:
        """Short alias for ``raw``."""

        return self.raw

    @property
    def cl(self) -> str:
        """Short alias for ``clean``."""

        return self.clean

    @property
    def pc(self) -> str:
        """Short alias for ``pascal``."""

        return self.pascal

    @property
    def cm(self) -> str:
        """Short alias for ``camel``."""

        return self.camel

    @property
    def sn(self) -> str:
        """Short alias for ``snake``."""

        return self.snake

    @property
    def kb(self) -> str:
        """Short alias for ``kebab``."""

        return self.kebab

    @property
    def ss(self) -> str:
        """Short alias for ``screaming_snake``."""

        return self.screaming_snake

    @property
    def cn(self) -> str:
        """Short alias for ``constant``."""

        return self.constant

    @property
    def pt(self) -> str:
        """Short alias for ``path``."""

        return self.path


@dataclass(frozen=True)
class SpecName:
    """Prepared naming context for a normalized spec item.

    Singular and plural are nested casing objects, so access is explicit:

    - ``name.singular.path``
    - ``name.singular.pascal``
    - ``name.plural.path``
    - ``name.plural.camel``

    Do not expose direct string fields like ``name.singular`` or
    ``name.plural``.
    """

    raw: str
    clean: str
    pascal: str
    camel: str
    snake: str
    kebab: str
    screaming_snake: str
    constant: str
    path: str
    singular: SpecNameCases
    plural: SpecNameCases

    @property
    def rw(self) -> str:
        """Short alias for ``raw``."""

        return self.raw

    @property
    def cl(self) -> str:
        """Short alias for ``clean``."""

        return self.clean

    @property
    def pc(self) -> str:
        """Short alias for ``pascal``."""

        return self.pascal

    @property
    def cm(self) -> str:
        """Short alias for ``camel``."""

        return self.camel

    @property
    def sn(self) -> str:
        """Short alias for ``snake``."""

        return self.snake

    @property
    def kb(self) -> str:
        """Short alias for ``kebab``."""

        return self.kebab

    @property
    def ss(self) -> str:
        """Short alias for ``screaming_snake``."""

        return self.screaming_snake

    @property
    def cn(self) -> str:
        """Short alias for ``constant``."""

        return self.constant

    @property
    def pt(self) -> str:
        """Short alias for ``path``."""

        return self.path


def resolve_name_case(name: SpecName, case: SpecNameCase) -> str:
    """Resolve a name case without dynamic attribute access."""

    if case == SpecNameCase.RAW:
        return name.raw
    if case == SpecNameCase.CLEAN:
        return name.clean
    if case == SpecNameCase.PASCAL:
        return name.pascal
    if case == SpecNameCase.CAMEL:
        return name.camel
    if case == SpecNameCase.SNAKE:
        return name.snake
    if case == SpecNameCase.KEBAB:
        return name.kebab
    if case == SpecNameCase.SCREAMING_SNAKE:
        return name.screaming_snake
    if case == SpecNameCase.CONSTANT:
        return name.constant
    if case == SpecNameCase.PATH:
        return name.path

    raise ValueError(f"Unsupported name case: {case}")
