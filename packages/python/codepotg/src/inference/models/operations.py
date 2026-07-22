"""Operation inference model types."""

from dataclasses import dataclass, field
from typing import Any

from inference.models.resources import InferredResource


@dataclass(frozen=True)
class InferredMediaType:
    """Inferred media type from content objects."""

    content_type: str
    schema_ref: str | None = None
    schema_refs: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class InferredParameter:
    """Inferred parameter from OpenAPI operations."""

    name: str
    location: str
    required: bool
    ref: str | None = None
    schema_ref: str | None = None
    schema_refs: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class InferredOperationTarget:
    """Inferred generic operation target from x-codegen.target metadata."""

    ref: str
    source: str
    exclude: tuple[str, ...] = field(default_factory=tuple)
    inferred_roles: tuple[str, ...] = field(default_factory=tuple)
    locations: tuple[str, ...] = field(default_factory=tuple)
    reason: str = ""


@dataclass(frozen=True)
class InferredParameterTarget:
    """Inferred parameter target from x-codegen parameter target metadata."""

    ref: str
    source: str
    locations: tuple[str, ...] = field(default_factory=tuple)
    parameter_names: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class InferredRequestBody:
    """Inferred request body from OpenAPI operations."""

    ref: str | None = None
    required: bool = False
    content_types: tuple[str, ...] = field(default_factory=tuple)
    media_types: tuple[InferredMediaType, ...] = field(default_factory=tuple)
    schema_refs: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class InferredResponse:
    """Inferred response from OpenAPI operations."""

    status_code: str
    ref: str | None = None
    description: str = ""
    content_types: tuple[str, ...] = field(default_factory=tuple)
    media_types: tuple[InferredMediaType, ...] = field(default_factory=tuple)
    schema_refs: tuple[str, ...] = field(default_factory=tuple)
    is_success: bool = False
    is_error: bool = False


@dataclass(frozen=True)
class InferredOperation:
    """Inferred operation from OpenAPI paths."""

    operation_id: str
    method: str
    path: str
    resource: "InferredResource | None" = None
    parameters: tuple[InferredParameter, ...] = field(default_factory=tuple)
    request_body: InferredRequestBody | None = None
    responses: tuple[InferredResponse, ...] = field(default_factory=tuple)
    target: InferredOperationTarget | None = None
    ui: dict[str, Any] = field(default_factory=dict)
    raw: dict[str, Any] = field(default_factory=dict)
