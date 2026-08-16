from __future__ import annotations

from dataclasses import dataclass, field

from dryv.ir import FieldCapabilities


@dataclass(frozen=True, slots=True)
class FieldOptions:
    required: bool = True
    nullable: bool = False
    readonly: bool = False
    minimum: int | float | None = None
    maximum: int | float | None = None
    min_length: int | None = None
    max_length: int | None = None
    pattern: str | None = None
    format: str | None = None

    def __post_init__(self) -> None:
        if self.minimum is not None and self.maximum is not None and self.minimum > self.maximum:
            raise ValueError("minimum must not exceed maximum")
        if self.min_length is not None and self.min_length < 0:
            raise ValueError("min_length must be non-negative")
        if self.max_length is not None and self.max_length < 0:
            raise ValueError("max_length must be non-negative")
        if self.min_length is not None and self.max_length is not None and self.min_length > self.max_length:
            raise ValueError("min_length must not exceed max_length")


@dataclass(frozen=True, slots=True)
class PropertyDeclaration:
    annotation: object
    options: FieldOptions = field(default_factory=FieldOptions)
    capabilities: FieldCapabilities = field(default_factory=FieldCapabilities)


__all__ = ["FieldOptions", "PropertyDeclaration"]
