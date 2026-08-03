"""Python language adapter constants."""

from __future__ import annotations

PYTHON_LANGUAGE_KEY = "python"
PYTHON_DEFAULT_EXTENSION = "py"

PYTHON_SOURCE_EXTENSIONS = (
    ".py",
    ".pyi",
)

DEFAULT_CLASS_CASE = "pascal"
DEFAULT_INTERFACE_CASE = "pascal"
DEFAULT_ENUM_CASE = "pascal"
DEFAULT_ENUM_VALUE_CASE = "constant"
DEFAULT_FIELD_CASE = "snake"
DEFAULT_METHOD_CASE = "snake"
DEFAULT_FUNCTION_CASE = "snake"
DEFAULT_CONSTANT_CASE = "screaming_snake"
DEFAULT_FILE_CASE = "snake"
DEFAULT_MODULE_CASE = "snake"
DEFAULT_PACKAGE_CASE = "snake"

DEFAULT_IMPORT_STRATEGY = "relative"
DEFAULT_INCLUDE_IMPORT_EXTENSION = False
DEFAULT_TYPE_ONLY_IMPORTS = False

PY_STR = "str"
PY_FLOAT = "float"
PY_INT = "int"
PY_BOOL = "bool"
PY_ANY = "Any"
PY_NONE = "None"

PRIMITIVE_STRING = "string"
PRIMITIVE_NUMBER = "number"
PRIMITIVE_INTEGER = "integer"
PRIMITIVE_BOOLEAN = "boolean"

RESERVED_WORD_SUFFIX = "_value"
RESERVED_WORD_ESCAPE_REASON = "reserved Python keyword"

PYTHON_RESERVED_WORDS: frozenset[str] = frozenset(
    {
        "False",
        "None",
        "True",
        "and",
        "as",
        "assert",
        "async",
        "await",
        "break",
        "class",
        "continue",
        "def",
        "del",
        "elif",
        "else",
        "except",
        "finally",
        "for",
        "from",
        "global",
        "if",
        "import",
        "in",
        "is",
        "lambda",
        "nonlocal",
        "not",
        "or",
        "pass",
        "raise",
        "return",
        "try",
        "while",
        "with",
        "yield",
        "match",
        "case",
        "type",
    }
)
