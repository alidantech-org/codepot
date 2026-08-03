"""Generic normalized spec record contracts."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Generic, TypeVar

from archives.codepot.src.contracts.spec.dependencies import SpecDependency
from archives.codepot.src.contracts.spec.names import SpecName
from archives.codepot.src.contracts.spec.refs import SpecIdentity, SpecOwner, SpecRef

TData = TypeVar("TData", covariant=True)


class SpecRecordKind(StrEnum):
    """Normalized record kinds exposed by the spec repository."""

    URL = "url"
    CONTENT_TYPE = "content_type"

    PRIMITIVE = "primitive"
    ENUM = "enum"
    COMPOSITE = "composite"

    ENTITY = "entity"
    FIELD_SET = "field_set"
    MODEL = "model"
    DTO = "dto"
    PARAMS = "params"

    RESOURCE = "resource"
    OPERATION = "operation"
    ROUTE_PATH = "route_path"
    ROUTE = "route"

    ERROR = "error"

    SECURITY_CREDENTIAL = "security_credential"
    SECURITY_PRINCIPAL = "security_principal"
    SECURITY_POLICY = "security_policy"


@dataclass(frozen=True)
class SpecRecord(Generic[TData]):
    """One normalized spec record.

    ``data`` is the original typed IR object. The repository adds the runtime
    metadata around it: key, ref, name, identity, owner, and dependencies.
    """
    id: str
    kind: SpecRecordKind
    key: str
    ref: SpecRef
    identity: SpecIdentity
    name: SpecName
    data: TData
    owner: SpecOwner
    dependencies: tuple[SpecDependency, ...] = ()


@dataclass(frozen=True)
class SpecRecordSet(Generic[TData]):
    """A normalized list of records from a map-shaped spec registry.

    Repository internals may keep indexes, but this public contract stays as a
    plain immutable list for simple looping in planning/template code.
    """

    kind: SpecRecordKind
    items: tuple[SpecRecord[TData], ...]
