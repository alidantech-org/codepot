from __future__ import annotations

from importlib import import_module
from typing import Any

from .diagnostics import (
    Diagnostic,
    Diagnostics,
    DiagnosticSeverity,
    SourceIdentity,
    SourceKind,
    SourcePosition,
    SourceSpan,
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
from .versions import (
    CORE_VERSION,
    DEFAULT_BEHAVIOR_VERSIONS,
    IR_API_VERSION,
    PUBLIC_API_VERSION,
    ApiVersion,
    BehaviorVersion,
    BehaviorVersions,
    Version,
)

__version__ = str(CORE_VERSION)

_LAZY_EXPORTS = {
    "DryvRuntime": ("dryv.runtime", "DryvRuntime"),
    "RuntimeSnapshot": ("dryv.runtime", "RuntimeSnapshot"),
    "contract_from_document": ("dryv.features.serialization", "contract_from_document"),
    "contract_from_json": ("dryv.features.serialization", "contract_from_json"),
    "contract_from_yaml": ("dryv.features.serialization", "contract_from_yaml"),
    "contract_to_document": ("dryv.features.serialization", "contract_to_document"),
    "contract_to_json": ("dryv.features.serialization", "contract_to_json"),
    "contract_to_yaml": ("dryv.features.serialization", "contract_to_yaml"),
    "create_runtime": ("dryv.runtime", "create_runtime"),
}


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
    "Contract",
    "ContractValidator",
    "DEFAULT_BEHAVIOR_VERSIONS",
    "Diagnostic",
    "DiagnosticSeverity",
    "Diagnostics",
    "DryvRuntime",
    "Group",
    "IR_API_VERSION",
    "Name",
    "NameProjection",
    "Operation",
    "PUBLIC_API_VERSION",
    "RuntimeSnapshot",
    "Schema",
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
    "create_runtime",
    "validate_contract",
]
