"""Base inference model types."""

from enum import StrEnum


class InferredSchemaKind(StrEnum):
    """Schema kind classification."""

    UNKNOWN = "unknown"
    ENUM = "enum"
    MODEL = "model"
    DTO = "dto"
    PRIMITIVE = "primitive"
