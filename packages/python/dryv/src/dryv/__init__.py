from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING, Any

from .api import CancellationToken, OperationCancelled, OperationResult, OperationStatus
from .diagnostics import (
    Diagnostic,
    Diagnostics,
    DiagnosticSeverity,
    SourceIdentity,
    SourceKind,
    SourcePosition,
    SourceSpan,
)
from .generation import (
    DEFAULT_SELECTOR_REGISTRY,
    SelectionCardinality,
    SelectionContext,
    SelectorDescriptor,
    SelectorRegistry,
)
from .ir import (
    Contract,
    ContractValidator,
    Group,
    Name,
    NameProjection,
    Operation,
    Schema,
    SemanticId,
    validate_contract,
)
from .plugins import PluginCategory, PluginDescriptor, PluginRegistry, PluginTrust
from .versions import (
    CORE_VERSION,
    DEFAULT_BEHAVIOR_VERSIONS,
    IR_API_VERSION,
    PLUGIN_API_VERSION,
    PUBLIC_API_VERSION,
    ApiVersion,
    BehaviorVersion,
    BehaviorVersions,
    Version,
)

__version__ = str(CORE_VERSION)

_LAZY_EXPORTS = {
    "contract_from_document": ("dryv.ir", "contract_from_document"),
    "contract_from_json": ("dryv.ir", "contract_from_json"),
    "contract_from_yaml": ("dryv.ir", "contract_from_yaml"),
    "contract_to_document": ("dryv.ir", "contract_to_document"),
    "contract_to_json": ("dryv.ir", "contract_to_json"),
    "contract_to_yaml": ("dryv.ir", "contract_to_yaml"),
    "generate": ("dryv.application", "generate"),
    "generate_to_files": ("dryv.runtime.composition", "generate_to_files"),
}

if TYPE_CHECKING:
    from .application import generate
    from .ir import (
        contract_from_document,
        contract_from_json,
        contract_from_yaml,
        contract_to_document,
        contract_to_json,
        contract_to_yaml,
    )
    from .runtime.composition import generate_to_files


def __getattr__(name: str) -> Any:
    target = _LAZY_EXPORTS.get(name)
    if target is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module_name, attribute = target
    value = getattr(import_module(module_name), attribute)
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    return sorted(set(globals()) | set(__all__))


__all__ = [
    "ApiVersion",
    "BehaviorVersion",
    "BehaviorVersions",
    "CORE_VERSION",
    "CancellationToken",
    "Contract",
    "ContractValidator",
    "DEFAULT_BEHAVIOR_VERSIONS",
    "DEFAULT_SELECTOR_REGISTRY",
    "Diagnostic",
    "DiagnosticSeverity",
    "Diagnostics",
    "Group",
    "IR_API_VERSION",
    "Name",
    "NameProjection",
    "Operation",
    "OperationCancelled",
    "OperationResult",
    "OperationStatus",
    "PLUGIN_API_VERSION",
    "PUBLIC_API_VERSION",
    "PluginCategory",
    "PluginDescriptor",
    "PluginRegistry",
    "PluginTrust",
    "Schema",
    "SelectionCardinality",
    "SelectionContext",
    "SelectorDescriptor",
    "SelectorRegistry",
    "SemanticId",
    "SourceIdentity",
    "SourceKind",
    "SourcePosition",
    "SourceSpan",
    "Version",
    "contract_from_document",
    "contract_from_json",
    "contract_from_yaml",
    "contract_to_document",
    "contract_to_json",
    "contract_to_yaml",
    "generate",
    "generate_to_files",
    "validate_contract",
]
