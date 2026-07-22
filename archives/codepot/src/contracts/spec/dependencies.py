"""Dependency contracts for normalized spec records."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from archives.codepot.src.contracts.spec.refs import SpecRef


class SpecDependencyKind(StrEnum):
    """Kinds of normalized spec dependencies."""

    REF = "ref"
    OWNER = "owner"
    EXTENDS = "extends"
    FIELD = "field"
    FIELD_ITEM = "field_item"
    RELATION = "relation"
    PARAMS = "params"
    QUERY = "query"
    BODY = "body"
    RESULT = "result"
    ERROR = "error"
    OPERATION = "operation"
    ROUTE_PATH = "route_path"
    ROUTE_METHOD = "route_method"
    CONTENT_TYPE = "content_type"
    SECURITY = "security"


@dataclass(frozen=True)
class SpecDependency:
    """One normalized dependency discovered from a spec record.

    The repository extracts these from refs in the typed IR payload. Planning
    later uses ``target.subject`` to resolve dependencies through template
    config ``resolves`` mappings.
    """

    source: SpecRef
    target: SpecRef
    kind: SpecDependencyKind
    required: bool = True
    label: str | None = None
