from __future__ import annotations

from dataclasses import dataclass

from codepotg.ir import FrozenObject, FrozenValue, KernelData, Provenance

from ..diagnostics import DiagnosticBag
from ..options import OpenApiOptions
from ..parsing.document import ParsedDocument


@dataclass(slots=True)
class PreservationBudget:
    remaining: int


class PreservationError(ValueError):
    pass


def kernel_data(
    document: ParsedDocument,
    pointer: str,
    *,
    options: OpenApiOptions,
    diagnostics: DiagnosticBag,
    raw: dict[str, object] | None = None,
    extensions: dict[str, object] | None = None,
) -> KernelData:
    return KernelData(
        provenance=Provenance(
            source_kind="openapi",
            source_id=document.source.logical_id,
            pointer=pointer,
            span=document.span(pointer),
        ),
        raw=_bounded_object(raw or {}, options, diagnostics, document, pointer, "raw"),
        extensions=_bounded_object(
            extensions or {},
            options,
            diagnostics,
            document,
            pointer,
            "extensions",
        ),
    )


def extension_values(value: dict[str, object]) -> dict[str, object]:
    return {key: item for key, item in value.items() if key.startswith("x-") and key != "x-codegen"}


def selected_raw(value: dict[str, object], *keys: str) -> dict[str, object]:
    return {key: value[key] for key in keys if key in value}


def _bounded_object(
    value: dict[str, object],
    options: OpenApiOptions,
    diagnostics: DiagnosticBag,
    document: ParsedDocument,
    pointer: str,
    label: str,
) -> FrozenObject:
    if not value:
        return ()
    budget = PreservationBudget(options.max_preserved_items)
    try:
        frozen = _freeze(value, 0, budget, options.max_preserved_depth)
    except PreservationError as exc:
        diagnostics.warning(
            "OA_LIMIT_PRESERVATION",
            f"{label} metadata was not preserved: {exc}",
            span=document.span(pointer),
        )
        return ()
    assert isinstance(frozen, tuple)
    return frozen


def _freeze(
    value: object,
    depth: int,
    budget: PreservationBudget,
    max_depth: int,
) -> FrozenValue:
    if depth > max_depth:
        raise PreservationError(f"depth exceeds maxPreservedDepth ({max_depth})")
    budget.remaining -= 1
    if budget.remaining < 0:
        raise PreservationError("item count exceeds maxPreservedItems")
    if value is None or isinstance(value, str | bool | int):
        return value
    if isinstance(value, float):
        if value != value or value in {float("inf"), float("-inf")}:
            raise PreservationError("non-finite number")
        return value
    if isinstance(value, list | tuple):
        return tuple(_freeze(item, depth + 1, budget, max_depth) for item in value)
    if isinstance(value, dict):
        if not all(isinstance(key, str) and key for key in value):
            raise PreservationError("object keys must be non-empty strings")
        return tuple(
            (key, _freeze(item, depth + 1, budget, max_depth))
            for key, item in sorted(value.items())
        )
    raise PreservationError(f"unsupported value type {type(value).__name__}")
