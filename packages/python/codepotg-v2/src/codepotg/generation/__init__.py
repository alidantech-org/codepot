from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING, Any

from codepotg.domain.generation import (
    DEFAULT_SELECTOR_REGISTRY,
    SelectionCardinality,
    SelectionContext,
    SelectorDescriptor,
    SelectorRegistry,
)

_LAZY_EXPORTS = {
    "ArtifactPlan": (".models", "ArtifactPlan"),
    "DiscoveredPackFile": (".models", "DiscoveredPackFile"),
    "ExpressionError": (".expressions", "ExpressionError"),
    "GeneratedArtifact": (".models", "GeneratedArtifact"),
    "GenerationData": (".models", "GenerationData"),
    "GenerationPlan": (".models", "GenerationPlan"),
    "MemoryOutput": (".models", "MemoryOutput"),
    "ModuleCollection": (".models", "ModuleCollection"),
    "ModuleDescriptor": (".models", "ModuleDescriptor"),
    "PackDiscoveryError": (".discovery", "PackDiscoveryError"),
    "PackFileKind": (".models", "PackFileKind"),
    "ProjectPlanner": (".planner", "ProjectPlanner"),
    "RenderContextBuilder": (".context", "RenderContextBuilder"),
    "discover_pack_files": (".discovery", "discover_pack_files"),
    "evaluate_text": (".expressions", "evaluate_text"),
    "explain_artifact": (".inspection", "explain_artifact"),
    "plan_to_document": (".inspection", "plan_to_document"),
    "plan_to_json": (".inspection", "plan_to_json"),
    "resolve_expression": (".expressions", "resolve_expression"),
}

if TYPE_CHECKING:
    from .context import RenderContextBuilder
    from .discovery import PackDiscoveryError, discover_pack_files
    from .expressions import ExpressionError, evaluate_text, resolve_expression
    from .inspection import explain_artifact, plan_to_document, plan_to_json
    from .models import (
        ArtifactPlan,
        DiscoveredPackFile,
        GeneratedArtifact,
        GenerationData,
        GenerationPlan,
        MemoryOutput,
        ModuleCollection,
        ModuleDescriptor,
        PackFileKind,
    )
    from .planner import ProjectPlanner


def __getattr__(name: str) -> Any:
    target = _LAZY_EXPORTS.get(name)
    if target is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module_name, attribute = target
    value = getattr(import_module(module_name, __name__), attribute)
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    return sorted(set(globals()) | set(__all__))


__all__ = [
    "ArtifactPlan",
    "DEFAULT_SELECTOR_REGISTRY",
    "DiscoveredPackFile",
    "ExpressionError",
    "GeneratedArtifact",
    "GenerationData",
    "GenerationPlan",
    "MemoryOutput",
    "ModuleCollection",
    "ModuleDescriptor",
    "PackDiscoveryError",
    "PackFileKind",
    "ProjectPlanner",
    "RenderContextBuilder",
    "SelectionCardinality",
    "SelectionContext",
    "SelectorDescriptor",
    "SelectorRegistry",
    "discover_pack_files",
    "evaluate_text",
    "explain_artifact",
    "plan_to_document",
    "plan_to_json",
    "resolve_expression",
]
