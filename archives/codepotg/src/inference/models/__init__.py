"""Inference model types.

This package contains dataclass models for representing inferred
OpenAPI structures including resources, schemas, operations, and dependencies.
"""

from archives.codepotg.src.inference.models.base import InferredSchemaKind
from archives.codepotg.src.inference.models.dependencies import InferredDependency
from archives.codepotg.src.inference.models.graph import InferenceGraph
from archives.codepotg.src.inference.models.operations import (
    InferredMediaType,
    InferredOperation,
    InferredOperationTarget,
    InferredParameter,
    InferredParameterTarget,
    InferredRequestBody,
    InferredResponse,
)
from archives.codepotg.src.inference.models.resources import InferredResource
from archives.codepotg.src.inference.models.schemas import InferredSchema

__all__ = [
    "InferredSchemaKind",
    "InferredDependency",
    "InferenceGraph",
    "InferredMediaType",
    "InferredOperation",
    "InferredOperationTarget",
    "InferredParameter",
    "InferredParameterTarget",
    "InferredRequestBody",
    "InferredResponse",
    "InferredResource",
    "InferredSchema",
]
