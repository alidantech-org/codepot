"""Dart language adapter constants."""

from __future__ import annotations

DART_LANGUAGE_KEY = "dart"
DART_DEFAULT_EXTENSION = "dart"

DART_SOURCE_EXTENSIONS = (".dart",)

DEFAULT_CLASS_CASE = "pascal"
DEFAULT_INTERFACE_CASE = "pascal"
DEFAULT_ENUM_CASE = "pascal"
DEFAULT_ENUM_VALUE_CASE = "camel"
DEFAULT_FIELD_CASE = "camel"
DEFAULT_METHOD_CASE = "camel"
DEFAULT_FUNCTION_CASE = "camel"
DEFAULT_CONSTANT_CASE = "camel"
DEFAULT_FILE_CASE = "snake"
DEFAULT_MODULE_CASE = "snake"
DEFAULT_PACKAGE_CASE = "snake"

DEFAULT_IMPORT_STRATEGY = "relative"
DEFAULT_INCLUDE_IMPORT_EXTENSION = True
DEFAULT_TYPE_ONLY_IMPORTS = False

DART_STRING = "String"
DART_DOUBLE = "double"
DART_INT = "int"
DART_BOOL = "bool"
DART_DYNAMIC = "dynamic"
DART_VOID = "void"

PRIMITIVE_STRING = "string"
PRIMITIVE_NUMBER = "number"
PRIMITIVE_INTEGER = "integer"
PRIMITIVE_BOOLEAN = "boolean"

RESERVED_WORD_SUFFIX = "Value"
RESERVED_WORD_ESCAPE_REASON = "reserved Dart keyword"

DART_RESERVED_WORDS: frozenset[str] = frozenset(
    {
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
        "of",
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
        "type",
        "typedef",
        "var",
        "void",
        "when",
        "while",
        "with",
        "yield",
    }
)
