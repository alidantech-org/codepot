"""Typed JSON reference models for compiled Codepot IR."""

from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

TargetT = TypeVar("TargetT")


class Ref(BaseModel, Generic[TargetT]):
    """Portable JSON/YAML reference used by compiled Codepot IR."""

    model_config = ConfigDict(frozen=True, extra="forbid", populate_by_name=True)

    ref: str = Field(alias="$ref")


RefLike = Ref[TargetT]
