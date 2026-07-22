"""TypeScript language adapter constants."""

from __future__ import annotations

# Language identity
TYPESCRIPT_LANGUAGE_KEY = "typescript"
TYPESCRIPT_DEFAULT_EXTENSION = "ts"

# File extensions
TYPESCRIPT_SOURCE_EXTENSIONS = (
    ".ts",
    ".tsx",
    ".js",
    ".jsx",
)

# Default naming cases
DEFAULT_CLASS_CASE = "pascal"
DEFAULT_INTERFACE_CASE = "pascal"
DEFAULT_ENUM_CASE = "pascal"
DEFAULT_ENUM_VALUE_CASE = "constant"
DEFAULT_FIELD_CASE = "camel"
DEFAULT_METHOD_CASE = "camel"
DEFAULT_FUNCTION_CASE = "camel"
DEFAULT_CONSTANT_CASE = "screaming_snake"
DEFAULT_FILE_CASE = "path"
DEFAULT_MODULE_CASE = "path"
DEFAULT_PACKAGE_CASE = "snake"

# Import defaults
DEFAULT_IMPORT_STRATEGY = "relative"
DEFAULT_INCLUDE_IMPORT_EXTENSION = False
DEFAULT_TYPE_ONLY_IMPORTS = False

# Render fragments
IMPORT_TYPE_KEYWORD = " type"
IMPORT_KEYWORD = "import"
EXPORT_KEYWORD = "export"
FROM_KEYWORD = "from"

# TypeScript type names
TS_STRING = "string"
TS_NUMBER = "number"
TS_BOOLEAN = "boolean"
TS_UNKNOWN = "unknown"
TS_VOID = "void"
TS_NULL = "null"

# Codepot primitive type values
PRIMITIVE_STRING = "string"
PRIMITIVE_NUMBER = "number"
PRIMITIVE_INTEGER = "integer"
PRIMITIVE_BOOLEAN = "boolean"

# Reserved keyword escape
RESERVED_WORD_SUFFIX = "Value"
RESERVED_WORD_ESCAPE_REASON = "reserved TypeScript keyword"

TYPESCRIPT_RESERVED_WORDS: frozenset[str] = frozenset(
    {
        "abstract",
        "any",
        "as",
        "asserts",
        "async",
        "await",
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
        "satisfies",
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
        "unknown",
        "var",
        "void",
        "while",
        "with",
        "yield",
    }
)
