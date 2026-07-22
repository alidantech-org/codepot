"""Inference graph model type."""

from dataclasses import dataclass
from typing import Any

from inference.models.dependencies import InferredDependency
from inference.models.operations import InferredOperation
from inference.models.resources import InferredResource
from inference.models.schemas import InferredSchema


@dataclass(frozen=True)
class InferenceGraph:
    """Complete inference graph containing all inferred data."""

    title: str
    openapi_version: str
    api_version: str
    description: str
    servers: tuple[dict[str, Any], ...]
    resources: tuple[InferredResource, ...]
    schemas: tuple[InferredSchema, ...]
    operations: tuple[InferredOperation, ...]
    dependencies: tuple[InferredDependency, ...]
    x_codegen: dict[str, Any] | None = None
