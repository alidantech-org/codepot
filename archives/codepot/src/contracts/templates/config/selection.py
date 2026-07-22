"""Template selection config contracts."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict


class TemplateSelectSubject(StrEnum):
    """Selectable template subjects."""

    CONTENT_TYPES = "content_types"

    ENUMS = "enums"
    COMPOSITES = "composites"

    ENTITIES = "entities"
    FIELD_SETS = "field_sets"
    MODELS = "models"
    DTOS = "dtos"

    RESOURCES = "resources"
    OPERATIONS = "operations"
    ROUTE_PATHS = "route_paths"
    ROUTES = "routes"

    ERRORS = "errors"

    SECURITY_CREDENTIALS = "security_credentials"
    SECURITY_PRINCIPALS = "security_principals"
    SECURITY_POLICIES = "security_policies"


class TemplateSelectMode(StrEnum):
    """How selected records become files."""

    ONCE = "once"
    EACH = "each"
    ALL = "all"
    BY_OWNER = "by_owner"


class TemplateSelect(BaseModel):
    """Parsed select expression.

    Raw config stores select as a string, for example ``models.each`` or
    ``once``. Route paths, routes, and operations should use ``*.by_owner``
    when they are grouped by their resource owner.
    """

    model_config = ConfigDict(frozen=True)

    raw: str
    subject: TemplateSelectSubject | None = None
    mode: TemplateSelectMode