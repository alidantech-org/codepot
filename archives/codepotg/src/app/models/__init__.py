"""Runtime input and output contracts.

These models define the public runtime interface used by CLI, tests, UI, API
servers, and other adapters.
"""

from archives.codepotg.src.app.models.diagnostics import RuntimeDiagnostic
from archives.codepotg.src.app.models.events import ProgressSink, RuntimeEvent
from archives.codepotg.src.app.models.inputs import (
    EmitInput,
    GenerateInput,
    InferInput,
    InspectInput,
    JsonlInput,
    PathsInput,
    ValidateInput,
)
from archives.codepotg.src.app.models.outputs import (
    AliasSchemaSummary,
    EmitOutput,
    GenerateOutput,
    GenerateTaskOutput,
    InferOutput,
    InspectOutput,
    JsonlOutput,
    PathBarrelSummary,
    PathEmissionSummary,
    PathFolderSummary,
    PathProviderSummary,
    PathSelectionSummary,
    PathsOutput,
    ResourceSummary,
    UnknownSchemaSummary,
    ValidateOutput,
)

__all__ = [
    "EmitInput",
    "GenerateInput",
    "InferInput",
    "InspectInput",
    "JsonlInput",
    "PathsInput",
    "ValidateInput",
    "EmitOutput",
    "GenerateOutput",
    "GenerateTaskOutput",
    "InferOutput",
    "InspectOutput",
    "JsonlOutput",
    "PathBarrelSummary",
    "PathEmissionSummary",
    "PathFolderSummary",
    "PathProviderSummary",
    "PathSelectionSummary",
    "PathsOutput",
    "ValidateOutput",
    "ResourceSummary",
    "UnknownSchemaSummary",
    "AliasSchemaSummary",
    "RuntimeDiagnostic",
    "RuntimeEvent",
    "ProgressSink",
]
