"""Dart-safe naming helpers."""

from __future__ import annotations

import re

from contracts.names import NameSet, make_contract_name

DART_RESERVED_WORDS = {
    "abstract",
    "as",
    "assert",
    "async",
    "await",
    "base",
    "break",
    "case",
    "catch",
    "class",
    "const",
    "continue",
    "covariant",
    "default",
    "deferred",
    "do",
    "dynamic",
    "else",
    "enum",
    "export",
    "extends",
    "extension",
    "external",
    "factory",
    "false",
    "final",
    "finally",
    "for",
    "function",
    "get",
    "hide",
    "if",
    "implements",
    "import",
    "in",
    "interface",
    "is",
    "late",
    "library",
    "mixin",
    "new",
    "null",
    "on",
    "operator",
    "part",
    "required",
    "rethrow",
    "return",
    "sealed",
    "set",
    "show",
    "static",
    "super",
    "switch",
    "sync",
    "this",
    "throw",
    "true",
    "try",
    "typedef",
    "var",
    "void",
    "when",
    "while",
    "with",
    "yield",
}

_IDENTIFIER_SPLIT_PATTERN = re.compile(r"[^A-Za-z0-9]+")
_IDENTIFIER_VALID_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_IDENTIFIER_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_PACKAGE_PATTERN = re.compile(r"^[a-z_][a-z0-9_]*$")


def safe_identifier(
    value: object,
    *,
    fallback: str = "value",
    reserved_words: set[str] | None = None,
) -> str:
    """Return a safe lowerCamel-like identifier from any value."""
    text = str(value or "").strip()

    if not text:
        return fallback

    parts = [part for part in _IDENTIFIER_SPLIT_PATTERN.split(text) if part]

    if not parts:
        return fallback

    if len(parts) == 1:
        name = _lower_first(parts[0])
    else:
        name = parts[0].lower() + "".join(part[:1].upper() + part[1:] for part in parts[1:])

    if name[0].isdigit():
        name = f"value{name[:1].upper()}{name[1:]}"

    if not _IDENTIFIER_VALID_PATTERN.match(name):
        name = fallback

    if reserved_words and name in reserved_words:
        name = f"{name}Value"

    return name


def _lower_first(value: str) -> str:
    return value[:1].lower() + value[1:]


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


def safe_dart_identifier(value: object, *, fallback: str = "value") -> str:
    """Return a Dart-safe identifier."""
    candidate = _clean_identifier(value, fallback=fallback)

    if candidate in DART_RESERVED_WORDS:
        return f"{candidate}Value"

    return candidate


def safe_dart_package_name(value: object, *, fallback: str = "generated_api") -> str:
    """Return a Dart-safe package name."""
    source = name_text(value, fallback=fallback)
    name = name_text(make_contract_name(source).snake, fallback=fallback)
    name = re.sub(r"[^a-z0-9_]", "_", name.lower())
    name = re.sub(r"_+", "_", name).strip("_") or fallback

    if name[0].isdigit():
        name = f"pkg_{name}"

    if not _PACKAGE_PATTERN.match(name):
        return fallback

    if name in DART_RESERVED_WORDS:
        return f"{name}_package"

    return name


def safe_contract_name(value: str, *, fallback: str = "value") -> NameSet:
    """Return a NameSet from a Dart-safe-ish source value."""
    cleaned = value or fallback
    return make_contract_name(cleaned)


def _clean_identifier(value: object, *, fallback: str) -> str:
    source = name_text(value, fallback=fallback)
    name = name_text(make_contract_name(source).camel, fallback=fallback)

    if not name:
        name = fallback

    name = re.sub(r"[^A-Za-z0-9_]", "_", name)

    if name[0].isdigit():
        name = f"value{name}"

    if not _IDENTIFIER_PATTERN.match(name):
        return fallback

    return name
