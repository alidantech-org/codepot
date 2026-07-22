from __future__ import annotations

from typing import Any

from constants.codegen import X_CODEGEN
from constants.openapi import SCHEMAS
from inference.models import InferredResource, InferredSchemaKind
from openapi.document import OpenApiDocument
from openapi.refs import get_ref


def infer_kind_from_ref_alias(
    schema: dict[str, Any],
    document: OpenApiDocument,
    seen: set[str] | None = None,
) -> InferredSchemaKind | None:
    ref = get_ref(schema)
    if ref is None or ref.section != SCHEMAS or ref.name is None:
        return None

    seen = seen or set()
    if ref.raw in seen:
        return None

    seen.add(ref.raw)

    target = document.schemas.get(ref.name)
    if not isinstance(target, dict):
        return None

    from inference.classifiers import classify_schema

    return classify_schema(ref.name, target, document=document, seen_refs=seen)


def infer_resource_from_ref_alias(
    schema: dict[str, Any],
    document: OpenApiDocument,
    seen: set[str] | None = None,
) -> InferredResource | None:
    ref = get_ref(schema)
    if ref is None or ref.section != SCHEMAS or ref.name is None:
        return None

    seen = seen or set()
    if ref.raw in seen:
        return None

    seen.add(ref.raw)

    target = document.schemas.get(ref.name)
    if not isinstance(target, dict):
        return None

    x_codegen = target.get(X_CODEGEN)
    if isinstance(x_codegen, dict):
        resource = _extract_resource(x_codegen, document)
        if resource is not None:
            return resource

    return infer_resource_from_ref_alias(target, document, seen)


def _extract_resource(
    x_codegen: dict[str, Any],
    document: OpenApiDocument,
) -> InferredResource | None:
    from inference.resources import extract_resource_from_x_codegen

    return extract_resource_from_x_codegen(x_codegen, document)
