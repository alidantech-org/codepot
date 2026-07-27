"""Typed Python authoring compiler for the CodepotG v2 semantic IR."""

from .author import Author
from .diagnostics import (
    AUTHOR_CORE_UNSUPPORTED,
    AuthorDiagnostic,
    AuthorDiagnostics,
    AuthorDiagnosticSeverity,
)
from .options import AuthorOptions, UnsupportedCorePolicy
from .schemas import (
    FieldDeclaration,
    FieldOptions,
    ProjectionStep,
    PropertyDeclaration,
    SchemaDeclaration,
    SchemaDeclarationKind,
    field,
)
from .refs import (
    EventRef,
    FieldRef,
    GroupRef,
    OperationRef,
    PolicyRef,
    PresentationRef,
    PropertyRef,
    Ref,
    RefIdentity,
    RefKind,
    RefUsage,
    SchemaRef,
    StorageRef,
    ValueSourceRef,
    ViewRef,
    WorkflowRef,
    WorkflowStepRef,
)

__version__ = "0.1.0a1"

__all__ = [
    "AUTHOR_CORE_UNSUPPORTED",
    "Author",
    "AuthorDiagnostic",
    "AuthorDiagnostics",
    "AuthorDiagnosticSeverity",
    "AuthorOptions",
    "EventRef",
    "FieldDeclaration",
    "FieldOptions",
    "FieldRef",
    "GroupRef",
    "OperationRef",
    "PolicyRef",
    "PresentationRef",
    "ProjectionStep",
    "PropertyDeclaration",
    "PropertyRef",
    "Ref",
    "RefIdentity",
    "RefKind",
    "RefUsage",
    "SchemaDeclaration",
    "SchemaDeclarationKind",
    "SchemaRef",
    "StorageRef",
    "UnsupportedCorePolicy",
    "ValueSourceRef",
    "ViewRef",
    "WorkflowRef",
    "WorkflowStepRef",
    "field",
    "__version__",
]
