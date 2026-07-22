from __future__ import annotations

from typing import Any

from constants.openapi import PARAM_IN, PARAM_NAME, REQUIRED, SCHEMA
from inference.models import InferredParameter
from openapi.document import OpenApiDocument
from openapi.refs import get_ref
from openapi.resolver.parameters import resolve_parameter


def infer_parameters(
    parameters: Any,
    _document: OpenApiDocument,
    inherited: tuple[InferredParameter, ...] = (),
) -> tuple[InferredParameter, ...]:
    """Infer parameters from operation or path level."""
    if not isinstance(parameters, list):
        return inherited

    result: list[InferredParameter] = list(inherited)

    for raw_param in parameters:
        if not isinstance(raw_param, dict):
            continue

        param = resolve_parameter(_document, raw_param)
        if not isinstance(param, dict):
            continue

        name = param.get(PARAM_NAME)
        location = param.get(PARAM_IN)
        required = param.get(REQUIRED, False)

        if not isinstance(name, str) or not isinstance(location, str):
            continue

        ref = get_ref(raw_param) or get_ref(param)
        schema_ref = _extract_schema_ref(param)

        result.append(
            InferredParameter(
                name=name,
                location=location,
                required=bool(required),
                ref=ref.raw if ref else None,
                schema_ref=schema_ref,
                schema_refs=tuple([schema_ref]) if schema_ref else (),
            )
        )

    return tuple(result)


def _extract_schema_ref(param: dict[str, Any]) -> str | None:
    """Extract schema ref from a parameter."""
    schema = param.get(SCHEMA)
    ref = get_ref(schema)
    return ref.raw if ref else None
