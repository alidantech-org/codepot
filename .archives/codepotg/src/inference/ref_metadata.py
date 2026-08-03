from __future__ import annotations

from typing import Any

from archives.codepotg.src.constants.openapi import SCHEMAS
from archives.codepotg.src.inference.models import InferredResource, InferredSchemaKind
from archives.codepotg.src.inference.resources import extract_resource_from_x_codegen
from archives.codepotg.src.openapi.document import OpenApiDocument
from archives.codepotg.src.openapi.refs import find_refs


def infer_kind_from_ref_alias(
    schema: dict[str, Any],
    document: OpenApiDocument,
    seen_refs: set[str] | None = None,
) -> InferredSchemaKind | None:
    from archives.codepotg.src.openapi.refs import get_ref

    if seen_refs is None:
        seen_refs = set()

    ref = get_ref(schema)
    if ref is None or not ref.is_component:
        return None

    if ref.raw in seen_refs:
        return None

    seen_refs.add(ref.raw)

    if ref.section != SCHEMAS:
        return None

    schema_name = ref.name
    target_schema = document.schemas.get(schema_name)

    if not isinstance(target_schema, dict):
        return None

    from archives.codepotg.src.inference.classifiers import classify_schema

    return classify_schema(schema_name, target_schema, document, seen_refs)


def infer_resource_from_ref_alias(
    schema: dict[str, Any],
    document: OpenApiDocument,
) -> InferredResource | None:
    refs = find_refs(schema)

    for ref in refs:
        if not ref.is_component:
            continue

        resource = _extract_resource_from_ref(ref, document)
        if resource is not None:
            return resource

    return None


def _extract_resource_from_ref(
    ref,
    document: OpenApiDocument,
):
    if ref.section != SCHEMAS:
        return None

    schema_name = ref.name
    schema = document.schemas.get(schema_name)

    if not isinstance(schema, dict):
        return None

    from archives.codepotg.src.constants.codegen import X_CODEGEN

    x_codegen = schema.get(X_CODEGEN)
    if not isinstance(x_codegen, dict):
        return None

    return extract_resource_from_x_codegen(x_codegen, document)
