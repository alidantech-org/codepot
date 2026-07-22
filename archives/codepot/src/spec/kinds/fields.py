"""Compiled spec field kind enums."""

from __future__ import annotations

from enum import StrEnum


class QueryOperator(StrEnum):
    """Supported field query operators."""

    EQ = "eq"
    NEQ = "neq"
    IN = "in"
    NOT_IN = "not_in"
    CONTAINS = "contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    GT = "gt"
    GTE = "gte"
    LT = "lt"
    LTE = "lte"
    BETWEEN = "between"
    EXISTS = "exists"


class FieldVisibilityLevel(StrEnum):
    """Supported field visibility levels."""

    PUBLIC = "public"
    INTERNAL = "internal"
    SECRET = "secret"
    AUTH = "auth"


class FieldPersistenceMode(StrEnum):
    """Supported persistence modes for entity fields."""

    STORED = "stored"
    VIRTUAL = "virtual"
    COMPUTED = "computed"


class EntityRelationKind(StrEnum):
    """Supported entity relation kinds."""

    BELONGS_TO = "belongs_to"
    HAS_ONE = "has_one"
    HAS_MANY = "has_many"
    MANY_TO_MANY = "many_to_many"
