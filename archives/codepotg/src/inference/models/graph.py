"""Inference graph model type."""

from dataclasses import dataclass, field
from typing import Any

from archives.codepotg.src.inference.models.dependencies import InferredDependency
from archives.codepotg.src.inference.models.operations import InferredOperation
from archives.codepotg.src.inference.models.resources import InferredResource
from archives.codepotg.src.inference.models.schemas import InferredSchema


@dataclass(frozen=True)
class InferenceGraph:
    """Complete inference graph containing all inferred and preserved source data."""

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
    raw: dict[str, Any] = field(default_factory=dict, repr=False, compare=False)
