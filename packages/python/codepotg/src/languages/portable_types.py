"""Typed target-language metadata shared by production adapters.

The adapters remain language-neutral at inference time. This module translates the
already-normalized schema facts into target spellings and package layouts.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping


@dataclass(frozen=True)
class PortableTypeSystem:
    """Deterministic target type, package, file, and layout conventions."""

    language: str
    file_extension: str
    scalar_types: Mapping[str, str]
    format_types: Mapping[str, str] = field(
        default_factory=lambda: MappingProxyType({})
    )
    array_template: str = "list[{item}]"
    map_template: str = "dict[str, {value}]"
    nullable_template: str = "{value} | None"
    unknown_type: str = "object"
    package_file: str = ""
    source_root: str = "src"
    package_root: tuple[str, ...] = ("package",)
    model_root: tuple[str, ...] = ("package", "src", "models")
    client_root: tuple[str, ...] = ("package", "src", "client")
    type_filenames: bool = False

    def resolve(
        self,
        raw_type: str | None,
        *,
        format: str | None = None,
        nullable: bool = False,
        item_type: str | None = None,
        value_type: str | None = None,
    ) -> str:
        """Resolve a normalized OpenAPI type into one target-language type."""

        if item_type is not None or raw_type == "array":
            resolved = self.array_template.format(item=item_type or self.unknown_type)
        elif value_type is not None:
            resolved = self.map_template.format(value=value_type)
        elif format and format in self.format_types:
            resolved = self.format_types[format]
        else:
            resolved = self.scalar_types.get(raw_type or "", self.unknown_type)

        if nullable:
            return self.nullable_template.format(value=resolved)
        return resolved

    def model_filename(self, name: Any) -> str:
        """Build one deterministic model source filename from a NameSet or string."""

        if self.type_filenames:
            stem = getattr(getattr(name, "pascal", None), "o", None)
        else:
            stem = getattr(getattr(name, "snake", None), "o", None)
        return f"{stem or str(name)}{self.file_extension}"


def _frozen(values: Mapping[str, str]) -> Mapping[str, str]:
    return MappingProxyType(dict(values))


PYTHON_TYPES = PortableTypeSystem(
    language="python",
    file_extension=".py",
    scalar_types=_frozen(
        {
            "string": "str",
            "integer": "int",
            "number": "float",
            "boolean": "bool",
            "object": "dict[str, object]",
            "null": "None",
        }
    ),
    format_types=_frozen(
        {
            "date": "datetime.date",
            "date-time": "datetime.datetime",
            "uuid": "uuid.UUID",
            "binary": "bytes",
            "byte": "bytes",
            "decimal": "decimal.Decimal",
        }
    ),
    array_template="list[{item}]",
    map_template="dict[str, {value}]",
    nullable_template="{value} | None",
    unknown_type="object",
    package_file="pyproject.toml",
    source_root="src",
    package_root=("package",),
    model_root=("package", "src", "portable_client", "models"),
    client_root=("package", "src", "portable_client", "client"),
)

JAVA_TYPES = PortableTypeSystem(
    language="java",
    file_extension=".java",
    scalar_types=_frozen(
        {
            "string": "String",
            "integer": "Long",
            "number": "Double",
            "boolean": "Boolean",
            "object": "Map<String, Object>",
            "null": "Void",
        }
    ),
    format_types=_frozen(
        {
            "date": "LocalDate",
            "date-time": "OffsetDateTime",
            "uuid": "UUID",
            "binary": "byte[]",
            "byte": "byte[]",
            "decimal": "BigDecimal",
            "int32": "Integer",
            "int64": "Long",
            "float": "Float",
            "double": "Double",
        }
    ),
    array_template="List<{item}>",
    map_template="Map<String, {value}>",
    nullable_template="{value}",
    unknown_type="Object",
    package_file="pom.xml",
    source_root="src/main/java",
    package_root=("package",),
    model_root=("package", "src", "main", "java", "generated", "models"),
    client_root=("package", "src", "main", "java", "generated", "client"),
    type_filenames=True,
)

CSHARP_TYPES = PortableTypeSystem(
    language="csharp",
    file_extension=".cs",
    scalar_types=_frozen(
        {
            "string": "string",
            "integer": "long",
            "number": "double",
            "boolean": "bool",
            "object": "Dictionary<string, object>",
            "null": "object?",
        }
    ),
    format_types=_frozen(
        {
            "date": "DateOnly",
            "date-time": "DateTimeOffset",
            "uuid": "Guid",
            "binary": "byte[]",
            "byte": "byte[]",
            "decimal": "decimal",
            "int32": "int",
            "int64": "long",
            "float": "float",
            "double": "double",
        }
    ),
    array_template="List<{item}>",
    map_template="Dictionary<string, {value}>",
    nullable_template="{value}?",
    unknown_type="object",
    package_file="GeneratedClient.csproj",
    source_root=".",
    package_root=("package",),
    model_root=("package", "Models"),
    client_root=("package", "Client"),
    type_filenames=True,
)

GO_TYPES = PortableTypeSystem(
    language="go",
    file_extension=".go",
    scalar_types=_frozen(
        {
            "string": "string",
            "integer": "int64",
            "number": "float64",
            "boolean": "bool",
            "object": "map[string]any",
            "null": "any",
        }
    ),
    format_types=_frozen(
        {
            "date": "time.Time",
            "date-time": "time.Time",
            "uuid": "uuid.UUID",
            "binary": "[]byte",
            "byte": "[]byte",
            "decimal": "decimal.Decimal",
            "int32": "int32",
            "int64": "int64",
            "float": "float32",
            "double": "float64",
        }
    ),
    array_template="[]{item}",
    map_template="map[string]{value}",
    nullable_template="*{value}",
    unknown_type="any",
    package_file="go.mod",
    source_root=".",
    package_root=("package",),
    model_root=("package", "models"),
    client_root=("package", "client"),
)

RUST_TYPES = PortableTypeSystem(
    language="rust",
    file_extension=".rs",
    scalar_types=_frozen(
        {
            "string": "String",
            "integer": "i64",
            "number": "f64",
            "boolean": "bool",
            "object": "serde_json::Value",
            "null": "()",
        }
    ),
    format_types=_frozen(
        {
            "date": "chrono::NaiveDate",
            "date-time": "chrono::DateTime<chrono::Utc>",
            "uuid": "uuid::Uuid",
            "binary": "Vec<u8>",
            "byte": "Vec<u8>",
            "decimal": "rust_decimal::Decimal",
            "int32": "i32",
            "int64": "i64",
            "float": "f32",
            "double": "f64",
        }
    ),
    array_template="Vec<{item}>",
    map_template="std::collections::BTreeMap<String, {value}>",
    nullable_template="Option<{value}>",
    unknown_type="serde_json::Value",
    package_file="Cargo.toml",
    source_root="src",
    package_root=("package",),
    model_root=("package", "src", "models"),
    client_root=("package", "src", "client"),
)

TYPE_SYSTEMS: Mapping[str, PortableTypeSystem] = MappingProxyType(
    {
        item.language: item
        for item in (PYTHON_TYPES, JAVA_TYPES, CSHARP_TYPES, GO_TYPES, RUST_TYPES)
    }
)


def type_system_for(language: str) -> PortableTypeSystem:
    """Return one registered production target type system."""

    try:
        return TYPE_SYSTEMS[language]
    except KeyError as error:
        raise ValueError(f"Unsupported portable target language: {language}") from error
