"""Resource inference model types."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class InferredResource:
    """Inferred resource from x-codegen metadata."""

    name: str
    path: tuple[str, ...] = field(default_factory=tuple)
