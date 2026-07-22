"""Reusable compiled spec kind enums."""

from archives.codepot.src.spec.kinds.content import ContentStrategy
from archives.codepot.src.spec.kinds.fields import (
    EntityRelationKind,
    FieldPersistenceMode,
    FieldVisibilityLevel,
    QueryOperator,
)
from archives.codepot.src.spec.kinds.primitive import PrimitiveFormat, PrimitiveType
from archives.codepot.src.spec.kinds.routes import HttpMethod
from archives.codepot.src.spec.kinds.security import (
    SecurityCredentialFormat,
    SecurityCredentialSource,
    SecurityPolicyMode,
)
from archives.codepot.src.spec.kinds.urls import UrlEnv, UrlKind, UrlProtocol

__all__ = (
    "ContentStrategy",
    "EntityRelationKind",
    "FieldPersistenceMode",
    "FieldVisibilityLevel",
    "HttpMethod",
    "PrimitiveFormat",
    "PrimitiveType",
    "QueryOperator",
    "SecurityCredentialFormat",
    "SecurityCredentialSource",
    "SecurityPolicyMode",
    "UrlEnv",
    "UrlKind",
    "UrlProtocol",
)
