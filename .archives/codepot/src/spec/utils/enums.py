"""Spec repository utility enums."""

from __future__ import annotations

from enum import StrEnum


class SpecSubject(StrEnum):
    """Selectable normalized spec subjects."""

    URLS = "urls"
    CONTENT_TYPES = "content_types"

    PRIMITIVES = "primitives"
    ENUMS = "enums"
    COMPOSITES = "composites"

    ENTITIES = "entities"
    FIELD_SETS = "field_sets"
    MODELS = "models"
    DTOS = "dtos"
    PARAMS = "params"

    RESOURCES = "resources"
    OPERATIONS = "operations"
    ROUTE_PATHS = "route_paths"
    ROUTES = "routes"

    ERRORS = "errors"

    SECURITY_CREDENTIALS = "security_credentials"
    SECURITY_PRINCIPALS = "security_principals"
    SECURITY_POLICIES = "security_policies"


class SpecSection(StrEnum):
    """Physical sections in the compiled Codepot IR document."""

    URLS = "urls"
    CONTENT_TYPES = "content_types"

    PROPERTIES_PRIMITIVES = "properties/primitives"
    PROPERTIES_ENUMS = "properties/enums"
    PROPERTIES_COMPOSITES = "properties/composites"

    SCHEMAS_ENTITIES = "schemas/entities"
    SCHEMAS_FIELD_SETS = "schemas/field_sets"
    SCHEMAS_MODELS = "schemas/models"
    SCHEMAS_DTOS = "schemas/dtos"
    SCHEMAS_PARAMS = "schemas/params"

    RESOURCES = "resources"
    RESPONSES_ERRORS = "responses/errors"

    SECURITY_CREDENTIALS = "security/credentials"
    SECURITY_PRINCIPALS = "security/principals"
    SECURITY_POLICIES = "security/policies"


class SpecIdentityPart(StrEnum):
    """Known identity parser parts."""

    OWNER_IDENTITY = "owner_identity"
    OWNER_KEY = "owner_key"
    LOCAL_KEY = "local_key"


class SpecHashKind(StrEnum):
    """Hash kinds used by repository/cache layers."""

    FILE = "file"
    SECTION = "section"
    RECORD = "record"
    EMISSION = "emission"
