from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import asdict, dataclass
from enum import StrEnum
from typing import Any

_PACKAGE = re.compile(r"^(?:@[a-z0-9][a-z0-9._-]*/)?[a-z0-9][a-z0-9._-]*$")
_ALIAS = re.compile(r"^(?:@|~|@?[A-Za-z_$][A-Za-z0-9_$-]*)(?:/[A-Za-z0-9_$.-]+)*$")


class ReservedWordPolicy(StrEnum):
    ERROR = "error"
    WARNING = "warning"


class UnicodeIdentifierPolicy(StrEnum):
    ASCII_ONLY = "asciiOnly"
    SPEC_VALIDATED = "specValidated"


class TypeScriptExtensionPolicy(StrEnum):
    PRESERVE = "preserve"
    OMIT_TYPESCRIPT = "omitTypeScript"


class IndexResolutionPolicy(StrEnum):
    PRESERVE = "preserve"
    OMIT_INDEX = "omitIndex"


@dataclass(frozen=True, slots=True, order=True)
class AliasBinding:
    alias: str
    root: str

    def __post_init__(self) -> None:
        if not isinstance(self.alias, str) or not isinstance(self.root, str):
            raise ValueError("TS_MODULE_ALIAS_INVALID: alias and root must be strings")
        if _ALIAS.fullmatch(self.alias) is None or any(
            character in self.alias for character in ("'", '"', "\n", "\r", "\0")
        ):
            raise ValueError("TS_MODULE_ALIAS_INVALID: invalid authored alias prefix")
        _validate_relative_root(self.root)


@dataclass(frozen=True, slots=True)
class TypeScriptTargetOptions:
    reserved_word_policy: ReservedWordPolicy = ReservedWordPolicy.ERROR
    unicode_identifier_policy: UnicodeIdentifierPolicy = UnicodeIdentifierPolicy.ASCII_ONLY
    extension_policy: TypeScriptExtensionPolicy = TypeScriptExtensionPolicy.OMIT_TYPESCRIPT
    index_policy: IndexResolutionPolicy = IndexResolutionPolicy.PRESERVE
    package_name: str | None = None
    aliases: tuple[AliasBinding, ...] = ()

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
            "extension_policy",
            self.extension_policy,
            TypeScriptExtensionPolicy,
        )
        _require_enum("index_policy", self.index_policy, IndexResolutionPolicy)

        if self.package_name is not None and not isinstance(self.package_name, str):
            raise ValueError("TS_MODULE_PACKAGE_INVALID: package_name must be a string or null")
        if self.package_name is not None and _PACKAGE.fullmatch(self.package_name) is None:
            raise ValueError("TS_MODULE_PACKAGE_INVALID: invalid npm-style package name")

        if not isinstance(self.aliases, tuple):
            raise ValueError(
                "TS_MODULE_ALIAS_INVALID: aliases must be a tuple of AliasBinding values"
            )
        if any(not isinstance(item, AliasBinding) for item in self.aliases):
            raise ValueError(
                "TS_MODULE_ALIAS_INVALID: aliases must contain only AliasBinding values"
            )
        if tuple(sorted(self.aliases)) != self.aliases:
            raise ValueError("TS_MODULE_ALIAS_INVALID: aliases must be sorted")

        alias_names = tuple(item.alias for item in self.aliases)
        roots = tuple(item.root for item in self.aliases)
        if len(alias_names) != len(set(alias_names)):
            raise ValueError("TS_MODULE_ALIAS_INVALID: duplicate aliases are not allowed")
        if len(roots) != len(set(roots)):
            raise ValueError("TS_MODULE_ALIAS_AMBIGUOUS: duplicate alias roots are ambiguous")

    def to_dict(self) -> dict[str, object]:
        return {
            "aliases": tuple(asdict(item) for item in self.aliases),
            "extension_policy": self.extension_policy.value,
            "index_policy": self.index_policy.value,
            "package_name": self.package_name,
            "reserved_word_policy": self.reserved_word_policy.value,
            "unicode_identifier_policy": self.unicode_identifier_policy.value,
        }

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> TypeScriptTargetOptions:
        if not isinstance(value, Mapping):
            raise ValueError("TypeScript options must be a mapping")

        allowed = {
            "aliases",
            "extension_policy",
            "index_policy",
            "package_name",
            "reserved_word_policy",
            "unicode_identifier_policy",
        }
        unknown = set(value) - allowed
        if unknown:
            raise ValueError(f"unknown TypeScript option fields: {sorted(unknown)!r}")

        aliases_raw = value.get("aliases", ())
        if not isinstance(aliases_raw, (list, tuple)):
            raise ValueError("aliases must be a list or tuple of alias bindings")
        aliases = tuple(sorted(_decode_alias(item) for item in aliases_raw))

        package_name = value.get("package_name")
        if package_name is not None and not isinstance(package_name, str):
            raise ValueError("package_name must be a string or null")

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
            extension_policy=TypeScriptExtensionPolicy(
                value.get(
                    "extension_policy",
                    TypeScriptExtensionPolicy.OMIT_TYPESCRIPT.value,
                )
            ),
            index_policy=IndexResolutionPolicy(
                value.get("index_policy", IndexResolutionPolicy.PRESERVE.value)
            ),
            package_name=package_name,
            aliases=aliases,
        )


def _require_enum(field_name: str, value: object, enum_type: type[StrEnum]) -> None:
    if not isinstance(value, enum_type):
        raise ValueError(f"{field_name} must be a {enum_type.__name__} value")


def _decode_alias(value: object) -> AliasBinding:
    if not isinstance(value, Mapping):
        raise ValueError("each alias binding must be a mapping")

    unknown = set(value) - {"alias", "root"}
    if unknown:
        raise ValueError(f"unknown alias binding fields: {sorted(unknown)!r}")
    if set(value) != {"alias", "root"}:
        raise ValueError("alias bindings require exactly alias and root")

    alias = value["alias"]
    root = value["root"]
    if not isinstance(alias, str) or not isinstance(root, str):
        raise ValueError("alias and root must be strings")
    return AliasBinding(alias=alias, root=root)


def _validate_relative_root(root: str) -> None:
    if not isinstance(root, str):
        raise ValueError("TS_MODULE_ALIAS_INVALID: root must be a string")
    if not root or root.startswith("/") or "\\" in root or "\0" in root:
        raise ValueError("TS_MODULE_ALIAS_INVALID: root must be a POSIX-relative path")

    parts = root.split("/")
    if any(part in {"", ".", ".."} for part in parts):
        raise ValueError(
            "TS_MODULE_ALIAS_INVALID: root cannot contain empty, dot, or traversal segments"
        )
