from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum


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
        if not self.id_separator:
            raise TypeError("id_separator must be a non-empty string")
        if any(char.isspace() for char in self.id_separator):
            raise ValueError("id_separator must not contain whitespace")
        if self.max_declarations < 1:
            raise ValueError("max_declarations must be a positive integer")

    @classmethod
    def from_mapping(cls, value: Mapping[str, object]) -> AuthorOptions:
        allowed = {"strict", "id_separator", "unsupported_core", "max_declarations"}
        unknown = sorted(set(value) - allowed)
        if unknown:
            raise ValueError(f"unknown author options: {', '.join(unknown)}")
        raw_policy = value.get("unsupported_core", UnsupportedCorePolicy.DIAGNOSTIC)
        if isinstance(raw_policy, UnsupportedCorePolicy):
            policy = raw_policy
        elif isinstance(raw_policy, str):
            try:
                policy = UnsupportedCorePolicy(raw_policy)
            except ValueError as exc:
                raise ValueError("unsupported_core must be 'error' or 'diagnostic'") from exc
        else:
            raise TypeError("unsupported_core must be a string or UnsupportedCorePolicy")
        strict = value.get("strict", True)
        separator = value.get("id_separator", "/")
        maximum = value.get("max_declarations", 10_000)
        if type(strict) is not bool:
            raise TypeError("strict must be bool")
        if not isinstance(separator, str):
            raise TypeError("id_separator must be str")
        if type(maximum) is not int:
            raise TypeError("max_declarations must be int")
        return cls(
            strict=strict,
            id_separator=separator,
            unsupported_core=policy,
            max_declarations=maximum,
        )
