from __future__ import annotations

from collections.abc import Mapping
from numbers import Number

from jinja2 import Undefined

from .descriptors import HelperDescriptor, HelperKind


def filter_default(value: object, default_value: object = "", boolean: bool = False) -> object:
    if isinstance(value, Undefined) or (boolean and not value):
        return default_value
    return value


def filter_join(value: object, delimiter: str = "") -> str:
    if not isinstance(delimiter, str):
        raise TypeError("join delimiter must be a string")
    if isinstance(value, str) or not isinstance(value, tuple):
        raise TypeError("join accepts only immutable tuple sequences")
    return delimiter.join(str(item) for item in value)


def filter_length(value: object) -> int:
    if not isinstance(value, (str, tuple, Mapping)):
        raise TypeError("length accepts strings, tuples, and immutable mappings")
    return len(value)


def filter_lower(value: object) -> str:
    if not isinstance(value, str):
        raise TypeError("lower accepts only strings")
    return value.lower()


def filter_upper(value: object) -> str:
    if not isinstance(value, str):
        raise TypeError("upper accepts only strings")
    return value.upper()


def filter_trim(value: object) -> str:
    if not isinstance(value, str):
        raise TypeError("trim accepts only strings")
    return value.strip()


def filter_replace(value: object, old: str, new: str, count: int | None = None) -> str:
    if not isinstance(value, str) or not isinstance(old, str) or not isinstance(new, str):
        raise TypeError("replace accepts string values")
    if count is None:
        return value.replace(old, new)
    if isinstance(count, bool) or not isinstance(count, int) or count < 0:
        raise TypeError("replace count must be a non-negative integer")
    return value.replace(old, new, count)


def filter_indent(
    value: object,
    width: int | str = 4,
    first: bool = False,
    blank: bool = False,
) -> str:
    if not isinstance(value, str):
        raise TypeError("indent accepts only strings")
    if isinstance(width, bool) or not isinstance(width, (int, str)):
        raise TypeError("indent width must be a string or non-negative integer")
    if isinstance(width, int):
        if width < 0:
            raise TypeError("indent width must be non-negative")
        prefix = " " * width
    else:
        prefix = width
    lines = value.splitlines(keepends=True)
    if not lines:
        return value
    result: list[str] = []
    for index, line in enumerate(lines):
        body = line.rstrip("\r\n")
        ending = line[len(body) :]
        should_indent = (first or index > 0) and (blank or bool(body))
        result.append((prefix if should_indent else "") + body + ending)
    return "".join(result)


def filter_sort(value: object, reverse: bool = False) -> tuple[object, ...]:
    if isinstance(value, str) or not isinstance(value, tuple):
        raise TypeError("sort accepts only immutable tuple sequences")
    if not value:
        return ()
    allowed = (str, int, float, bool)
    if not all(isinstance(item, allowed) for item in value):
        raise TypeError("sort accepts only scalar tuple values")
    kinds = {type(item) for item in value}
    if len(kinds) > 1:
        raise TypeError("sort requires homogeneous scalar values")
    return tuple(sorted(value, reverse=bool(reverse)))


def filter_unique(value: object) -> tuple[object, ...]:
    if isinstance(value, str) or not isinstance(value, tuple):
        raise TypeError("unique accepts only immutable tuple sequences")
    result: list[object] = []
    seen: set[object] = set()
    for item in value:
        try:
            already_seen = item in seen
        except TypeError as exc:
            raise TypeError("unique values must be immutable and hashable") from exc
        if not already_seen:
            seen.add(item)
            result.append(item)
    return tuple(result)


def test_defined(value: object) -> bool:
    return not isinstance(value, Undefined)


def test_undefined(value: object) -> bool:
    return isinstance(value, Undefined)


def test_none(value: object) -> bool:
    return value is None


def test_boolean(value: object) -> bool:
    return isinstance(value, bool)


def test_integer(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def test_float(value: object) -> bool:
    return isinstance(value, float)


def test_number(value: object) -> bool:
    return isinstance(value, Number) and not isinstance(value, bool)


def test_string(value: object) -> bool:
    return isinstance(value, str)


def test_sequence(value: object) -> bool:
    return isinstance(value, tuple)


def test_mapping(value: object) -> bool:
    return isinstance(value, Mapping)


def test_equalto(value: object, other: object) -> bool:
    return value == other


def builtin_descriptors() -> tuple[HelperDescriptor, ...]:
    entries = (
        HelperDescriptor("default", "default", HelperKind.FILTER, "1", filter_default),
        HelperDescriptor("indent", "indent", HelperKind.FILTER, "1", filter_indent),
        HelperDescriptor("join", "join", HelperKind.FILTER, "1", filter_join),
        HelperDescriptor("length", "length", HelperKind.FILTER, "1", filter_length),
        HelperDescriptor("lower", "lower", HelperKind.FILTER, "1", filter_lower),
        HelperDescriptor("replace", "replace", HelperKind.FILTER, "1", filter_replace),
        HelperDescriptor("sort", "sort", HelperKind.FILTER, "1", filter_sort),
        HelperDescriptor("trim", "trim", HelperKind.FILTER, "1", filter_trim),
        HelperDescriptor("unique", "unique", HelperKind.FILTER, "1", filter_unique),
        HelperDescriptor("upper", "upper", HelperKind.FILTER, "1", filter_upper),
        HelperDescriptor("boolean", "boolean", HelperKind.TEST, "1", test_boolean),
        HelperDescriptor("defined", "defined", HelperKind.TEST, "1", test_defined),
        HelperDescriptor("equalto", "equalto", HelperKind.TEST, "1", test_equalto),
        HelperDescriptor("float", "float", HelperKind.TEST, "1", test_float),
        HelperDescriptor("integer", "integer", HelperKind.TEST, "1", test_integer),
        HelperDescriptor("mapping", "mapping", HelperKind.TEST, "1", test_mapping),
        HelperDescriptor("none", "none", HelperKind.TEST, "1", test_none),
        HelperDescriptor("number", "number", HelperKind.TEST, "1", test_number),
        HelperDescriptor("sequence", "sequence", HelperKind.TEST, "1", test_sequence),
        HelperDescriptor("string", "string", HelperKind.TEST, "1", test_string),
        HelperDescriptor("undefined", "undefined", HelperKind.TEST, "1", test_undefined),
    )
    return tuple(sorted(entries, key=HelperDescriptor.identity))
