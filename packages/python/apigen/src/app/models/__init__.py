"""Runtime input and output contracts.

These models define the public runtime interface used by CLI, tests, UI, API
servers, and other adapters.
"""

from app.models.diagnostics import RuntimeDiagnostic
from app.models.events import ProgressSink, RuntimeEvent
from app.models.inputs import EmitInput, GenerateInput, InferInput, InspectInput, ValidateInput
from app.models.outputs import (
    AliasSchemaSummary,
    EmitOutput,
    GenerateOutput,
    GenerateTaskOutput,
    InferOutput,
    InspectOutput,
    ResourceSummary,
    UnknownSchemaSummary,
    ValidateOutput,
)

__all__ = [
    "EmitInput",
    "GenerateInput",
    "InferInput",
    "InspectInput",
    "ValidateInput",
    "EmitOutput",
    "GenerateOutput",
    "GenerateTaskOutput",
    "InferOutput",
    "InspectOutput",
    "ValidateOutput",
    "ResourceSummary",
    "UnknownSchemaSummary",
    "AliasSchemaSummary",
    "RuntimeDiagnostic",
    "RuntimeEvent",
    "ProgressSink",
]
