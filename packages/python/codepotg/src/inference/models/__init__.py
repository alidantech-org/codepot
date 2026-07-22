"""Inference model types.

This package contains dataclass models for representing inferred
OpenAPI structures including resources, schemas, operations, and dependencies.
"""

from inference.models.base import InferredSchemaKind
from inference.models.dependencies import InferredDependency
from inference.models.graph import InferenceGraph
from inference.models.operations import (
    InferredMediaType,
    InferredOperation,
    InferredOperationTarget,
    InferredParameter,
    InferredParameterTarget,
    InferredRequestBody,
    InferredResponse,
)
from inference.models.resources import InferredResource
from inference.models.schemas import InferredSchema

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
