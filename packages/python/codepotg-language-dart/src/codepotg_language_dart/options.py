from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

_PACKAGE = re.compile(r"^[a-z][a-z0-9_]*$")


class ReservedWordPolicy(StrEnum):
    ERROR = "error"
    WARNING = "warning"


class UnicodeIdentifierPolicy(StrEnum):
    ASCII_ONLY = "asciiOnly"
    SPEC_VALIDATED = "specValidated"


class PrivateIdentifierPolicy(StrEnum):
    ALLOW_WITH_FACT = "allowWithFact"
    ALLOW_SILENT = "allowSilent"
    REQUIRE_PUBLIC = "requirePublic"


@dataclass(frozen=True, slots=True)
class DartTargetOptions:
    reserved_word_policy: ReservedWordPolicy = ReservedWordPolicy.ERROR
    unicode_identifier_policy: UnicodeIdentifierPolicy = (
        UnicodeIdentifierPolicy.ASCII_ONLY
    )
    private_identifier_policy: PrivateIdentifierPolicy = (
        PrivateIdentifierPolicy.ALLOW_WITH_FACT
    )
    package_name: str | None = None
    prefer_package_uris: bool = False

    def __post_init__(self) -> None:
        _require_enum(
            "reserved_word_policy",
            self.reserved_word_policy,
            ReservedWordPolicy,
        )
        _require_enum(
            "unicode_identifier_policy",
            self.unicode_identifier_policy,
            UnicodeIdentifierPolicy,
        )
        _require_enum(
            "private_identifier_policy",
            self.private_identifier_policy,
            PrivateIdentifierPolicy,
        )

        if self.package_name is not None and not isinstance(self.package_name, str):
            raise ValueError(
                "DART_MODULE_PACKAGE_INVALID: package_name must be a string or null"
            )
        if (
            self.package_name is not None
            and _PACKAGE.fullmatch(self.package_name) is None
        ):
            raise ValueError("DART_MODULE_PACKAGE_INVALID: invalid Dart package name")
        if not isinstance(self.prefer_package_uris, bool):
            raise ValueError("prefer_package_uris must be a boolean")

    def to_dict(self) -> dict[str, object]:
        return {
            "package_name": self.package_name,
            "prefer_package_uris": self.prefer_package_uris,
            "private_identifier_policy": self.private_identifier_policy.value,
            "reserved_word_policy": self.reserved_word_policy.value,
            "unicode_identifier_policy": self.unicode_identifier_policy.value,
        }

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> DartTargetOptions:
        if not isinstance(value, Mapping):
            raise ValueError("Dart options must be a mapping")

        allowed = {
            "package_name",
            "prefer_package_uris",
            "private_identifier_policy",
            "reserved_word_policy",
            "unicode_identifier_policy",
        }
        unknown = set(value) - allowed
        if unknown:
            raise ValueError(f"unknown Dart option fields: {sorted(unknown)!r}")

        package_name = value.get("package_name")
        if package_name is not None and not isinstance(package_name, str):
            raise ValueError("package_name must be a string or null")

        prefer_package_uris = value.get("prefer_package_uris", False)
        if not isinstance(prefer_package_uris, bool):
            raise ValueError("prefer_package_uris must be a boolean")

        return cls(
            reserved_word_policy=ReservedWordPolicy(
                value.get("reserved_word_policy", ReservedWordPolicy.ERROR.value)
            ),
            unicode_identifier_policy=UnicodeIdentifierPolicy(
                value.get(
                    "unicode_identifier_policy",
                    UnicodeIdentifierPolicy.ASCII_ONLY.value,
                )
            ),
            private_identifier_policy=PrivateIdentifierPolicy(
                value.get(
                    "private_identifier_policy",
                    PrivateIdentifierPolicy.ALLOW_WITH_FACT.value,
                )
            ),
            package_name=package_name,
            prefer_package_uris=prefer_package_uris,
        )


def _require_enum(field_name: str, value: object, enum_type: type[StrEnum]) -> None:
    if not isinstance(value, enum_type):
        raise ValueError(f"{field_name} must be a {enum_type.__name__} value")
