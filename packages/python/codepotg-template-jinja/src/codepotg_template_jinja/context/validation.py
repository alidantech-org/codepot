from __future__ import annotations

import math
import re
from dataclasses import fields, is_dataclass
from enum import Enum
from types import ModuleType
from typing import Any

from codepotg import diagnostics as public_diagnostics
from codepotg import ir as public_ir
from codepotg.ir import Group, Name, NameProjection

from codepotg_template_jinja.rules import JinjaEngineRules

from .access import SafeRecord, SafeValue

_CONTEXT_KEY = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")
_NAME_CASES = (
    "raw",
    "clean",
    "snake",
    "kebab",
    "camel",
    "pascal",
    "screaming",
    "constant",
    "dot",
    "path",
    "lower",
    "upper",
)


class ContextSafetyError(ValueError):
    def __init__(self, code: str, message: str, *, path: str, value_type: str) -> None:
        super().__init__(message)
        self.code = code
        self.path = path
        self.value_type = value_type


class _FreezeState:
    def __init__(self, rules: JinjaEngineRules) -> None:
        self.rules = rules
        self.items = 0
        self.active_ids: set[int] = set()

    def consume(self, path: str) -> None:
        self.items += 1
        if self.items > self.rules.max_context_items:
            raise ContextSafetyError(
                "JINJA_CONTEXT_LIMIT",
                "template context exceeds the configured item limit",
                path=path,
                value_type="context",
            )


def freeze_context(
    context: tuple[tuple[str, object], ...],
    rules: JinjaEngineRules,
) -> SafeRecord:
    state = _FreezeState(rules)
    keys = tuple(key for key, _ in context)
    if tuple(sorted(keys)) != keys or len(keys) != len(set(keys)):
        raise ContextSafetyError(
            "JINJA_CONTEXT_UNSAFE",
            "template context keys must be sorted and unique",
            path="$",
            value_type="context",
        )
    frozen: list[tuple[str, SafeValue]] = []
    for key, value in context:
        _validate_context_key(key, path=f"$.{key}")
        frozen.append((key, _freeze(value, state=state, depth=1, path=f"$.{key}")))
    return SafeRecord(tuple(frozen))


def _validate_context_key(key: str, *, path: str) -> None:
    if _CONTEXT_KEY.fullmatch(key) is None or key.startswith("_"):
        raise ContextSafetyError(
            "JINJA_CONTEXT_UNSAFE",
            "template context keys must be public identifier names",
            path=path,
            value_type="str",
        )


def _freeze(value: object, *, state: _FreezeState, depth: int, path: str) -> SafeValue:
    if depth > state.rules.max_context_depth:
        raise ContextSafetyError(
            "JINJA_CONTEXT_LIMIT",
            "template context exceeds the configured depth limit",
            path=path,
            value_type=type(value).__name__,
        )
    state.consume(path)

    if value is None:
        return value
    if isinstance(value, Enum):
        if not _is_approved_enum(value):
            raise ContextSafetyError(
                "JINJA_CONTEXT_UNSAFE",
                "enum values must come from an approved public CodepotG contract",
                path=path,
                value_type=type(value).__name__,
            )
        return _freeze(value.value, state=state, depth=depth + 1, path=f"{path}.value")
    if isinstance(value, (bool, int)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ContextSafetyError(
                "JINJA_CONTEXT_UNSAFE",
                "non-finite floats are not safe template context values",
                path=path,
                value_type="float",
            )
        return value
    if isinstance(value, str):
        try:
            value.encode("utf-8", errors="strict")
        except UnicodeEncodeError as exc:
            raise ContextSafetyError(
                "JINJA_CONTEXT_UNSAFE",
                "template context strings must be valid UTF-8",
                path=path,
                value_type="str",
            ) from exc
        return value
    if callable(value):
        raise ContextSafetyError(
            "JINJA_CALLABLE_DENIED",
            "callables supplied through template context are denied",
            path=path,
            value_type=type(value).__name__,
        )
    if isinstance(value, (type, ModuleType)):
        raise ContextSafetyError(
            "JINJA_CONTEXT_UNSAFE",
            "classes and modules are not safe template context values",
            path=path,
            value_type=type(value).__name__,
        )
    if isinstance(value, Name):
        return _freeze_name(value, state=state, depth=depth, path=path)
    if isinstance(value, NameProjection):
        return _freeze_projection(value, state=state, depth=depth, path=path)
    if isinstance(value, tuple):
        return _freeze_tuple(value, state=state, depth=depth, path=path)
    if _is_public_ir_dataclass_instance(value):
        return _freeze_dataclass(value, state=state, depth=depth, path=path)
    if _is_helper_descriptor(value):
        return _freeze_helper_descriptor(value, state=state, depth=depth, path=path)

    raise ContextSafetyError(
        "JINJA_CONTEXT_UNSAFE",
        "unsupported Python object in template context",
        path=path,
        value_type=type(value).__name__,
    )


def _freeze_name(value: Name, *, state: _FreezeState, depth: int, path: str) -> SafeRecord:
    # Name projections use cached_property. Read them from a fresh public Name clone so
    # validation never mutates the caller's original Name.__dict__.
    clone = Name(value.value)
    items: list[tuple[str, SafeValue]] = [("value", value.value)]
    for case in _NAME_CASES:
        projection = getattr(clone, case)
        items.append(
            (
                case,
                _freeze_projection(
                    projection,
                    state=state,
                    depth=depth + 1,
                    path=f"{path}.{case}",
                ),
            )
        )
    return SafeRecord(tuple(sorted(items)))


def _freeze_projection(
    value: NameProjection,
    *,
    state: _FreezeState,
    depth: int,
    path: str,
) -> SafeRecord:
    state.consume(path)
    items = (
        ("o", value.original),
        ("original", value.original),
        ("p", value.plural),
        ("plural", value.plural),
        ("s", value.singular),
        ("singular", value.singular),
    )
    return SafeRecord(items)


def _freeze_tuple(
    value: tuple[object, ...],
    *,
    state: _FreezeState,
    depth: int,
    path: str,
) -> SafeValue:
    object_id = id(value)
    _enter_compound(state, object_id, path, value)
    try:
        if value and all(
            isinstance(item, tuple)
            and len(item) == 2
            and isinstance(item[0], str)
            for item in value
        ):
            pairs = value
            keys = tuple(item[0] for item in pairs)
            if tuple(sorted(keys)) != keys or len(keys) != len(set(keys)):
                raise ContextSafetyError(
                    "JINJA_CONTEXT_UNSAFE",
                    "nested tuple-pair mappings must be sorted by unique key",
                    path=path,
                    value_type="tuple",
                )
            frozen_pairs: list[tuple[str, SafeValue]] = []
            for key, item in pairs:
                _validate_context_key(key, path=f"{path}.{key}")
                frozen_pairs.append(
                    (
                        key,
                        _freeze(item, state=state, depth=depth + 1, path=f"{path}.{key}"),
                    )
                )
            return SafeRecord(tuple(frozen_pairs))
        return tuple(
            _freeze(item, state=state, depth=depth + 1, path=f"{path}[{index}]")
            for index, item in enumerate(value)
        )
    finally:
        state.active_ids.remove(object_id)


def _freeze_dataclass(
    value: object,
    *,
    state: _FreezeState,
    depth: int,
    path: str,
) -> SafeRecord:
    object_id = id(value)
    _enter_compound(state, object_id, path, value)
    try:
        items: list[tuple[str, SafeValue]] = []
        for item in fields(value):
            if item.name.startswith("_"):
                continue
            field_value = getattr(value, item.name)
            items.append(
                (
                    item.name,
                    _freeze(
                        field_value,
                        state=state,
                        depth=depth + 1,
                        path=f"{path}.{item.name}",
                    ),
                )
            )
        if isinstance(value, Group):
            items.append(
                (
                    "storage",
                    _freeze(
                        value.storage,
                        state=state,
                        depth=depth + 1,
                        path=f"{path}.storage",
                    ),
                )
            )
        return SafeRecord(tuple(sorted(items)))
    finally:
        state.active_ids.remove(object_id)


def _freeze_helper_descriptor(
    value: Any,
    *,
    state: _FreezeState,
    depth: int,
    path: str,
) -> SafeRecord:
    public_items = (
        ("documentation", value.documentation),
        ("id", value.id),
        ("kind", value.kind.value),
        ("name", value.name),
        ("pure", value.pure),
        ("version", value.version),
    )
    return SafeRecord(
        tuple(
            (
                key,
                _freeze(item, state=state, depth=depth + 1, path=f"{path}.{key}"),
            )
            for key, item in public_items
        )
    )


def _enter_compound(state: _FreezeState, object_id: int, path: str, value: object) -> None:
    if object_id in state.active_ids:
        raise ContextSafetyError(
            "JINJA_CONTEXT_UNSAFE",
            "recursive object graphs are not safe template context values",
            path=path,
            value_type=type(value).__name__,
        )
    state.active_ids.add(object_id)


def _is_public_ir_dataclass_instance(value: object) -> bool:
    if not is_dataclass(value):
        return False
    params = getattr(type(value), "__dataclass_params__", None)
    if params is None or not params.frozen:
        return False
    for module in (public_ir, public_diagnostics):
        for name in getattr(module, "__all__", ()):
            candidate = getattr(module, name, None)
            if isinstance(candidate, type) and type(value) is candidate:
                return True
    return False


def _is_approved_enum(value: Enum) -> bool:
    for module in (public_ir, public_diagnostics):
        for name in getattr(module, "__all__", ()):
            candidate = getattr(module, name, None)
            if (
                isinstance(candidate, type)
                and issubclass(candidate, Enum)
                and type(value) is candidate
            ):
                return True
    from codepotg_template_jinja.helpers.descriptors import HelperKind

    return isinstance(value, HelperKind)


def _is_helper_descriptor(value: object) -> bool:
    from codepotg_template_jinja.helpers.descriptors import HelperDescriptor

    return isinstance(value, HelperDescriptor)
