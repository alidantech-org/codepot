"""Template dependency resolver config contracts."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class TemplateResolveRef(BaseModel):
    """JSON/YAML ref to a template entry or its barrel.

    Valid examples:
    - ``#/templates/enums``
    - ``#/templates/enums/barrel``
    """

    model_config = ConfigDict(frozen=True, populate_by_name=True)

    ref: str = Field(alias="$ref")


TemplateResolveMap = dict[str, TemplateResolveRef]