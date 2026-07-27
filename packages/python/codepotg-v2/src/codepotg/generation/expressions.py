from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import is_dataclass
from enum import Enum

from codepotg.ir import SemanticId

_EXPRESSION = re.compile(r"\(([^()]+)\)")
_LEFT_LITERAL = "\u0000codepot-left-paren\u0000"
_RIGHT_LITERAL = "\u0000codepot-right-paren\u0000"


class ExpressionError(ValueError):
    def __init__(self, code: str, message: str, *, expression: str) -> None:
        super().__init__(message)
        self.code = code
        self.expression = expression
        self.message = message


def evaluate_text(text: str, context: tuple[tuple[str, object], ...]) -> str:
    protected = text.replace("((", _LEFT_LITERAL).replace("))", _RIGHT_LITERAL)
    values = dict(context)

    def replace(match: re.Match[str]) -> str:
        expression = match.group(1).strip()
        if not expression:
            raise ExpressionError(
                "PATH_EXPRESSION_EMPTY",
                "path expressions cannot be empty",
                expression=expression,
            )
        value = resolve_expression(expression, values)
        return _stringify(value, expression)

    rendered = _EXPRESSION.sub(replace, protected)
    if "(" in rendered or ")" in rendered:
        raise ExpressionError(
            "PATH_EXPRESSION_SYNTAX",
            "unescaped or nested parentheses are not valid path expressions",
            expression=text,
        )
    return rendered.replace(_LEFT_LITERAL, "(").replace(_RIGHT_LITERAL, ")")


def resolve_expression(expression: str, roots: Mapping[str, object]) -> object:
    parts = tuple(part for part in expression.split(".") if part)
    if not parts or parts[0] not in roots:
        raise ExpressionError(
            "PATH_EXPRESSION_ROOT",
            f"unknown expression root {parts[0] if parts else expression!r}",
            expression=expression,
        )
    value: object = roots[parts[0]]
    for part in parts[1:]:
        value = _get(value, part, expression)
    return value


def _get(value: object, part: str, expression: str) -> object:
    if isinstance(value, tuple) and value and all(
        isinstance(item, tuple) and len(item) == 2 and isinstance(item[0], str)
        for item in value
    ):
        mapping = dict(value)
        if part not in mapping:
            raise _missing(part, expression)
        return mapping[part]
    if isinstance(value, Mapping):
        if part not in value:
            raise _missing(part, expression)
        return value[part]
    if isinstance(value, Enum) and part == "value":
        return value.value
    if isinstance(value, SemanticId) and part == "value":
        return value.value
    if is_dataclass(value) or type(value).__module__.startswith("codepotg"):
        if part.startswith("_") or not hasattr(value, part):
            raise _missing(part, expression)
        resolved = getattr(value, part)
        if callable(resolved):
            raise ExpressionError(
                "PATH_EXPRESSION_CALLABLE",
                "path expressions cannot access callables",
                expression=expression,
            )
        return resolved
    raise ExpressionError(
        "PATH_EXPRESSION_TYPE",
        f"cannot traverse {type(value).__name__} in a path expression",
        expression=expression,
    )


def _stringify(value: object, expression: str) -> str:
    if isinstance(value, SemanticId):
        return value.value
    if isinstance(value, Enum):
        return str(value.value)
    if value is None or isinstance(value, (tuple, Mapping)):
        raise ExpressionError(
            "PATH_EXPRESSION_VALUE",
            "path expressions must resolve to a scalar value",
            expression=expression,
        )
    if isinstance(value, (str, bool, int, float)):
        return str(value)
    raise ExpressionError(
        "PATH_EXPRESSION_VALUE",
        f"unsupported path expression value {type(value).__name__}",
        expression=expression,
    )


def _missing(part: str, expression: str) -> ExpressionError:
    return ExpressionError(
        "PATH_EXPRESSION_PROPERTY",
        f"unknown expression property {part!r}",
        expression=expression,
    )
