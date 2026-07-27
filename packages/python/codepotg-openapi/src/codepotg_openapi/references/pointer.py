from __future__ import annotations

from urllib.parse import unquote


class JsonPointerError(ValueError):
    pass


def normalize_fragment(fragment: str) -> str:
    decoded = unquote(fragment)
    if decoded == "":
        return ""
    if not decoded.startswith("/"):
        raise JsonPointerError("JSON Pointer fragments must be empty or start with '/'")
    segments = decoded.split("/")[1:]
    return "/" + "/".join(_escape(_decode(segment)) for segment in segments)


def resolve_pointer(value: object, pointer: str) -> object:
    if pointer == "":
        return value
    if not pointer.startswith("/"):
        raise JsonPointerError("JSON Pointer must be empty or start with '/'")
    current = value
    for encoded in pointer.split("/")[1:]:
        segment = _decode(encoded)
        if isinstance(current, dict):
            if segment not in current:
                raise JsonPointerError(f"JSON Pointer target segment {segment!r} does not exist")
            current = current[segment]
            continue
        if isinstance(current, list):
            if segment == "-" or not segment.isdigit():
                raise JsonPointerError(f"invalid array index {segment!r}")
            index = int(segment)
            if index >= len(current):
                raise JsonPointerError(f"array index {index} is out of range")
            current = current[index]
            continue
        raise JsonPointerError(f"cannot traverse segment {segment!r} through a scalar value")
    return current


def join_pointer(base: str, *segments: str | int) -> str:
    suffix = "/".join(_escape(str(segment)) for segment in segments)
    if not suffix:
        return base
    return f"{base}/{suffix}" if base else f"/{suffix}"


def _decode(segment: str) -> str:
    result: list[str] = []
    index = 0
    while index < len(segment):
        char = segment[index]
        if char != "~":
            result.append(char)
            index += 1
            continue
        if index + 1 >= len(segment) or segment[index + 1] not in {"0", "1"}:
            raise JsonPointerError(f"malformed JSON Pointer escape in {segment!r}")
        result.append("~" if segment[index + 1] == "0" else "/")
        index += 2
    return "".join(result)


def _escape(segment: str) -> str:
    return segment.replace("~", "~0").replace("/", "~1")
