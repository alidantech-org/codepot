from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import TypeAlias

from codepotg.ir import FrozenObject


class ValidationPolicy(StrEnum):
    STRICT = "strict"
    TOLERANT = "tolerant"


class ExternalReferencePolicy(StrEnum):
    DENY = "deny"
    LOCAL_ONLY = "localOnly"
    CONTROLLED = "controlled"


class GroupingPolicy(StrEnum):
    TAGS = "tags"
    EXPLICIT_THEN_TAGS = "explicitThenTags"


class MultiTagPolicy(StrEnum):
    FIRST = "first"
    EXPLICIT_REQUIRED = "explicitRequired"


class OperationIdPolicy(StrEnum):
    REQUIRE = "require"
    DETERMINISTIC_FALLBACK = "deterministicFallback"


class XCodegenPolicy(StrEnum):
    DENY = "deny"
    TOLERANT = "tolerant"
    STRICT = "strict"


OptionScalar: TypeAlias = str | int | bool


class OptionDecodeError(ValueError):
    def __init__(self, key: str, message: str) -> None:
        super().__init__(f"{key}: {message}")
        self.key = key
        self.message = message


@dataclass(frozen=True, slots=True)
class OpenApiOptions:
    validation: ValidationPolicy = ValidationPolicy.STRICT
    external_references: ExternalReferencePolicy = ExternalReferencePolicy.LOCAL_ONLY
    grouping: GroupingPolicy = GroupingPolicy.EXPLICIT_THEN_TAGS
    multi_tag_policy: MultiTagPolicy = MultiTagPolicy.FIRST
    operation_ids: OperationIdPolicy = OperationIdPolicy.DETERMINISTIC_FALLBACK
    x_codegen_policy: XCodegenPolicy = XCodegenPolicy.TOLERANT
    max_source_bytes: int = 8 * 1024 * 1024
    max_reference_depth: int = 64
    max_documents: int = 128
    preserve_unknown_extensions: bool = False
    max_preserved_depth: int = 8
    max_preserved_items: int = 2048

    @classmethod
    def decode(cls, value: FrozenObject) -> OpenApiOptions:
        raw = dict(value)
        defaults = cls()
        allowed = {
            "validation",
            "externalReferences",
            "grouping",
            "multiTagPolicy",
            "operationIds",
            "xCodegenPolicy",
            "maxSourceBytes",
            "maxReferenceDepth",
            "maxDocuments",
            "preserveUnknownExtensions",
            "maxPreservedDepth",
            "maxPreservedItems",
        }
        unknown = sorted(set(raw) - allowed)
        if unknown:
            raise OptionDecodeError(unknown[0], "unknown option")

        return cls(
            validation=_enum(raw, "validation", ValidationPolicy, defaults.validation),
            external_references=_enum(
                raw,
                "externalReferences",
                ExternalReferencePolicy,
                defaults.external_references,
            ),
            grouping=_enum(raw, "grouping", GroupingPolicy, defaults.grouping),
            multi_tag_policy=_enum(
                raw,
                "multiTagPolicy",
                MultiTagPolicy,
                defaults.multi_tag_policy,
            ),
            operation_ids=_enum(
                raw,
                "operationIds",
                OperationIdPolicy,
                defaults.operation_ids,
            ),
            x_codegen_policy=_enum(
                raw,
                "xCodegenPolicy",
                XCodegenPolicy,
                defaults.x_codegen_policy,
            ),
            max_source_bytes=_positive_int(
                raw,
                "maxSourceBytes",
                defaults.max_source_bytes,
            ),
            max_reference_depth=_positive_int(
                raw,
                "maxReferenceDepth",
                defaults.max_reference_depth,
            ),
            max_documents=_positive_int(raw, "maxDocuments", defaults.max_documents),
            preserve_unknown_extensions=_bool(
                raw,
                "preserveUnknownExtensions",
                defaults.preserve_unknown_extensions,
            ),
            max_preserved_depth=_positive_int(
                raw,
                "maxPreservedDepth",
                defaults.max_preserved_depth,
            ),
            max_preserved_items=_positive_int(
                raw,
                "maxPreservedItems",
                defaults.max_preserved_items,
            ),
        )

    def canonical_items(self) -> tuple[tuple[str, OptionScalar], ...]:
        return (
            ("externalReferences", self.external_references.value),
            ("grouping", self.grouping.value),
            ("maxDocuments", self.max_documents),
            ("maxPreservedDepth", self.max_preserved_depth),
            ("maxPreservedItems", self.max_preserved_items),
            ("maxReferenceDepth", self.max_reference_depth),
            ("maxSourceBytes", self.max_source_bytes),
            ("multiTagPolicy", self.multi_tag_policy.value),
            ("operationIds", self.operation_ids.value),
            ("preserveUnknownExtensions", self.preserve_unknown_extensions),
            ("validation", self.validation.value),
            ("xCodegenPolicy", self.x_codegen_policy.value),
        )


def _enum(
    raw: dict[str, object],
    key: str,
    enum_type: type[StrEnum],
    default: StrEnum,
) -> StrEnum:
    if key not in raw:
        return default
    value = raw[key]
    if not isinstance(value, str):
        raise OptionDecodeError(key, "must be a string")
    try:
        return enum_type(value)
    except ValueError as exc:
        choices = ", ".join(item.value for item in enum_type)
        raise OptionDecodeError(key, f"must be one of: {choices}") from exc


def _positive_int(raw: dict[str, object], key: str, default: int) -> int:
    if key not in raw:
        return default
    value = raw[key]
    if isinstance(value, bool) or not isinstance(value, int):
        raise OptionDecodeError(key, "must be an integer")
    if value < 1:
        raise OptionDecodeError(key, "must be positive")
    return value


def _bool(raw: dict[str, object], key: str, default: bool) -> bool:
    if key not in raw:
        return default
    value = raw[key]
    if not isinstance(value, bool):
        raise OptionDecodeError(key, "must be a boolean")
    return value
