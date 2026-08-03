"""Dependency inference model types."""

from dataclasses import dataclass


@dataclass(frozen=True)
class InferredDependency:
    """Inferred dependency between schema refs."""
    source_ref: str
    target_ref: str
