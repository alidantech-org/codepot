from __future__ import annotations

from typing import Any

from archives.codepotg.src.constants.codegen import X_CODEGEN
from archives.codepotg.src.inference.models import InferredResource
from archives.codepotg.src.inference.resources import extract_resource_from_x_codegen
from archives.codepotg.src.openapi.document import OpenApiDocument


def infer_resource(
    operation: dict[str, Any],
    path_item: dict[str, Any],
    path_resource: InferredResource | None,
    document: OpenApiDocument,
) -> InferredResource | None:
    """Infer resource ownership from operation and path metadata."""
    operation_resource = extract_resource_from_x_codegen(operation.get(X_CODEGEN, {}), document)
    return operation_resource or path_resource
