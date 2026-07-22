"""TypeScript-safe naming helpers."""

from __future__ import annotations

import re

from contracts.names import NameSet, make_contract_name

TYPESCRIPT_RESERVED_WORDS = {
    "abstract",
    "any",
    "as",
    "asserts",
    "async",
    "await",
    "bigint",
    "boolean",
    "break",
    "case",
    "catch",
    "class",
    "const",
    "constructor",
    "continue",
    "debugger",
    "declare",
    "default",
    "delete",
    "do",
    "else",
    "enum",
    "export",
    "extends",
    "false",
    "finally",
    "for",
    "from",
    "function",
    "get",
    "global",
    "if",
    "implements",
    "import",
    "in",
    "infer",
    "instanceof",
    "interface",
    "is",
    "keyof",
    "let",
    "module",
    "namespace",
    "never",
    "new",
    "null",
    "number",
    "object",
    "of",
    "package",
    "private",
    "protected",
    "public",
    "readonly",
    "require",
    "return",
    "set",
    "static",
    "string",
    "super",
    "switch",
    "symbol",
    "this",
    "throw",
    "true",
    "try",
    "type",
    "typeof",
    "undefined",
    "unique",
    "unknown",
    "var",
    "void",
    "while",
    "with",
    "yield",
}

_IDENTIFIER_SPLIT_PATTERN = re.compile(r"[^A-Za-z0-9]+")
_IDENTIFIER_PATTERN = re.compile(r"^[A-Za-z_$][A-Za-z0-9_$]*$")
_PACKAGE_PATTERN = re.compile(r"^(@[a-z0-9][a-z0-9._-]*/)?[a-z0-9][a-z0-9._-]*$")


def safe_identifier(
    value: object,
    *,
    fallback: str = "value",
    reserved_words: set[str] | None = None,
) -> str:
    """Return a safe lowerCamel TypeScript identifier from any value."""
    text = str(value or "").strip()

    if not text:
        return fallback

    parts = [part for part in _IDENTIFIER_SPLIT_PATTERN.split(text) if part]
    if not parts:
        return fallback

    if len(parts) == 1 and parts[0].isupper():
        name = parts[0].lower()
    elif len(parts) == 1:
        name = _lower_first(parts[0])
    else:
        name = parts[0].lower() + "".join(_upper_first(part) for part in parts[1:])

    if name[0].isdigit():
        name = f"value{_upper_first(name)}"

    if not _IDENTIFIER_PATTERN.match(name):
        name = fallback

    if reserved_words and name in reserved_words:
        return f"{name}Value"

    return name


def safe_enum_key(
    value: object,
    *,
    fallback: str = "value",
    reserved_words: set[str] | None = None,
) -> str:
    """Return a safe enum key while preserving common API semantics."""
    text = str(value or "").strip()

    if text.startswith("+") and len(text) > 1:
        base = safe_identifier(text[1:], fallback=fallback, reserved_words=reserved_words)
        return f"{base}Asc"

    if text.startswith("-") and len(text) > 1:
        base = safe_identifier(text[1:], fallback=fallback, reserved_words=reserved_words)
        return f"{base}Desc"

    if text == "+":
        return "plus"

    if text == "-":
        return "minus"

    return safe_identifier(text, fallback=fallback, reserved_words=reserved_words)


def name_text(value: object, *, fallback: str = "value") -> str:
    """Return a plain string from NameSet/PluralizedName/string values."""
    if value is None:
        return fallback

    if isinstance(value, str):
        return value or fallback

    raw = getattr(value, "value", None)
    if isinstance(raw, str) and raw:
        return raw

    original = getattr(value, "original", None)
    if isinstance(original, str) and original:
        return original

    text = str(value)
    return text if text and text != "None" else fallback


def safe_ts_identifier(value: object, *, fallback: str = "value") -> str:
    """Return a TypeScript-safe identifier."""
    candidate = _clean_identifier(value, fallback=fallback)

    if candidate in TYPESCRIPT_RESERVED_WORDS:
        return f"{candidate}Value"

    return candidate


def safe_ts_type_name(value: object, *, fallback: str = "GeneratedType") -> str:
    """Return a TypeScript-safe PascalCase type name."""
    source = name_text(value, fallback=fallback)
    name = name_text(make_contract_name(source).pascal, fallback=fallback)
    name = re.sub(r"[^A-Za-z0-9_$]", "", name)

    if not name:
        name = fallback

    if name[0].isdigit():
        name = f"Type{name}"

    if name[:1].islower():
        name = _upper_first(name)

    if name in TYPESCRIPT_RESERVED_WORDS:
        return f"{name}Type"

    return name


def safe_ts_package_name(value: object, *, fallback: str = "generated-api") -> str:
    """Return an npm-safe package name."""
    source = name_text(value, fallback=fallback)
    name = name_text(make_contract_name(source).kebab, fallback=fallback)
    name = re.sub(r"[^a-z0-9._@/-]", "-", name.lower())
    name = re.sub(r"-+", "-", name).strip("-") or fallback

    if name.startswith("@"):
        if "/" not in name:
            return fallback
        scope, package = name.split("/", 1)
        scope = scope.strip("@").strip(".-_")
        package = package.strip(".-_")
        name = f"@{scope}/{package}"

    if not _PACKAGE_PATTERN.match(name):
        return fallback

    return name


def safe_contract_name(value: str, *, fallback: str = "value") -> NameSet:
    """Return a NameSet from a TypeScript-safe-ish source value."""
    return make_contract_name(value or fallback)


def _clean_identifier(value: object, *, fallback: str) -> str:
    source = name_text(value, fallback=fallback)
    name = name_text(make_contract_name(source).camel, fallback=fallback)
    name = re.sub(r"[^A-Za-z0-9_$]", "_", name)

    if not name:
        name = fallback

    if name[0].isdigit():
        name = f"value{name}"

    if not _IDENTIFIER_PATTERN.match(name):
        return fallback

    return name


def _upper_first(value: str) -> str:
    if not value:
        return value

    return value[:1].upper() + value[1:]


def _lower_first(value: str) -> str:
    if not value:
        return value

    return value[:1].lower() + value[1:]
