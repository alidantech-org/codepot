from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Mapping


class UnsupportedCorePolicy(StrEnum):
    ERROR = "error"
    DIAGNOSTIC = "diagnostic"


@dataclass(frozen=True, slots=True)
class AuthorOptions:
    strict: bool = True
    id_separator: str = "/"
    unsupported_core: UnsupportedCorePolicy = UnsupportedCorePolicy.DIAGNOSTIC
    max_declarations: int = 10_000

    def __post_init__(self) -> None:
        if type(self.strict) is not bool:
            raise TypeError("strict must be bool")
        if not isinstance(self.id_separator, str) or not self.id_separator:
            raise TypeError("id_separator must be a non-empty string")
        if any(char.isspace() for char in self.id_separator):
            raise ValueError("id_separator must not contain whitespace")
        if not isinstance(self.unsupported_core, UnsupportedCorePolicy):
            raise TypeError("unsupported_core must be UnsupportedCorePolicy")
        if type(self.max_declarations) is not int or self.max_declarations < 1:
            raise ValueError("max_declarations must be a positive integer")

    @classmethod
    def from_mapping(cls, value: Mapping[str, object]) -> AuthorOptions:
        allowed = {"strict", "id_separator", "unsupported_core", "max_declarations"}
        unknown = sorted(set(value) - allowed)
        if unknown:
            raise ValueError(f"unknown author options: {', '.join(unknown)}")
        raw_policy = value.get("unsupported_core", UnsupportedCorePolicy.DIAGNOSTIC)
        try:
            policy = (
                raw_policy
                if isinstance(raw_policy, UnsupportedCorePolicy)
                else UnsupportedCorePolicy(raw_policy)
            )
        except (TypeError, ValueError) as exc:
            raise ValueError("unsupported_core must be 'error' or 'diagnostic'") from exc
        return cls(
            strict=value.get("strict", True),  # type: ignore[arg-type]
            id_separator=value.get("id_separator", "/"),  # type: ignore[arg-type]
            unsupported_core=policy,
            max_declarations=value.get("max_declarations", 10_000),  # type: ignore[arg-type]
        )
