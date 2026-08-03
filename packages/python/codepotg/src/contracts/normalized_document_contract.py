"""Typed, lossless top-level OpenAPI document contract.

This module gives templates named access to every standard top-level OpenAPI 3.x
family while retaining raw and extension escape hatches on every major object.
It is additive to the established compatibility and normalized domain contracts.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any

from archives.codepotg.src.contracts.normalized import (
    PresenceValue,
    SourceObject,
    presence_from_mapping,
    source_object,
)
from archives.codepotg.src.contracts.source import FrozenMap, freeze_source_map


@dataclass(frozen=True)
class NormalizedContactContract:
    source: SourceObject = field(default_factory=SourceObject)
    name: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    url: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    email: PresenceValue[Any] = field(default_factory=PresenceValue.missing)


@dataclass(frozen=True)
class NormalizedLicenseContract:
    source: SourceObject = field(default_factory=SourceObject)
    name: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    identifier: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    url: PresenceValue[Any] = field(default_factory=PresenceValue.missing)


@dataclass(frozen=True)
class NormalizedInfoContract:
    source: SourceObject = field(default_factory=SourceObject)
    title: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    summary: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    description: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    terms_of_service: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    contact: NormalizedContactContract = field(default_factory=NormalizedContactContract)
    license: NormalizedLicenseContract = field(default_factory=NormalizedLicenseContract)
    version: PresenceValue[Any] = field(default_factory=PresenceValue.missing)


@dataclass(frozen=True)
class NormalizedServerVariableContract:
    name: str
    source: SourceObject = field(default_factory=SourceObject)
    default: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    description: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    enum: tuple[Any, ...] = ()


@dataclass(frozen=True)
class NormalizedServerContract:
    source: SourceObject = field(default_factory=SourceObject)
    url: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    description: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    variables: Mapping[str, NormalizedServerVariableContract] = field(
        default_factory=lambda: MappingProxyType({})
    )


@dataclass(frozen=True)
class NormalizedExternalDocsContract:
    source: SourceObject = field(default_factory=SourceObject)
    description: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    url: PresenceValue[Any] = field(default_factory=PresenceValue.missing)


@dataclass(frozen=True)
class NormalizedTagContract:
    source: SourceObject = field(default_factory=SourceObject)
    name: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    description: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    external_docs: NormalizedExternalDocsContract = field(
        default_factory=NormalizedExternalDocsContract
    )


@dataclass(frozen=True)
class NormalizedPathItemContract:
    name: str
    source: SourceObject = field(default_factory=SourceObject)
    summary: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    description: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    ref: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    servers: tuple[NormalizedServerContract, ...] = ()
    parameters: tuple[FrozenMap, ...] = ()
    operations: Mapping[str, SourceObject] = field(
        default_factory=lambda: MappingProxyType({})
    )


@dataclass(frozen=True)
class NormalizedComponentsContract:
    source: SourceObject = field(default_factory=SourceObject)
    schemas: Mapping[str, SourceObject] = field(default_factory=lambda: MappingProxyType({}))
    responses: Mapping[str, SourceObject] = field(default_factory=lambda: MappingProxyType({}))
    parameters: Mapping[str, SourceObject] = field(default_factory=lambda: MappingProxyType({}))
    examples: Mapping[str, SourceObject] = field(default_factory=lambda: MappingProxyType({}))
    request_bodies: Mapping[str, SourceObject] = field(default_factory=lambda: MappingProxyType({}))
    headers: Mapping[str, SourceObject] = field(default_factory=lambda: MappingProxyType({}))
    security_schemes: Mapping[str, SourceObject] = field(default_factory=lambda: MappingProxyType({}))
    links: Mapping[str, SourceObject] = field(default_factory=lambda: MappingProxyType({}))
    callbacks: Mapping[str, SourceObject] = field(default_factory=lambda: MappingProxyType({}))
    path_items: Mapping[str, SourceObject] = field(default_factory=lambda: MappingProxyType({}))


@dataclass(frozen=True)
class NormalizedOpenApiDocumentContract:
    source: SourceObject = field(default_factory=SourceObject)
    openapi: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    json_schema_dialect: PresenceValue[Any] = field(default_factory=PresenceValue.missing)
    info: NormalizedInfoContract = field(default_factory=NormalizedInfoContract)
    servers: tuple[NormalizedServerContract, ...] = ()
    paths: Mapping[str, NormalizedPathItemContract] = field(
        default_factory=lambda: MappingProxyType({})
    )
    webhooks: Mapping[str, NormalizedPathItemContract] = field(
        default_factory=lambda: MappingProxyType({})
    )
    components: NormalizedComponentsContract = field(default_factory=NormalizedComponentsContract)
    security: tuple[FrozenMap, ...] = ()
    tags: tuple[NormalizedTagContract, ...] = ()
    external_docs: NormalizedExternalDocsContract = field(
        default_factory=NormalizedExternalDocsContract
    )

    @property
    def extensions(self) -> FrozenMap:
        return self.source.extensions

    @property
    def raw(self) -> FrozenMap:
        return self.source.raw

    @property
    def diagnostics(self):
        return self.source.diagnostics

    @property
    def loss_count(self) -> int:
        return self.source.loss_count


def build_normalized_document_contract(
    raw: Mapping[str, Any] | None,
) -> NormalizedOpenApiDocumentContract:
    document = _mapping(raw)
    return NormalizedOpenApiDocumentContract(
        source=source_object(
            document,
            source_path="$",
            known_keys={
                "openapi",
                "jsonSchemaDialect",
                "info",
                "servers",
                "paths",
                "webhooks",
                "components",
                "security",
                "tags",
                "externalDocs",
                "x-codegen",
            },
        ),
        openapi=presence_from_mapping(document, "openapi", source_path="$"),
        json_schema_dialect=presence_from_mapping(
            document,
            "jsonSchemaDialect",
            source_path="$",
        ),
        info=_info(_mapping(document.get("info"))),
        servers=tuple(
            _server(_mapping(value), index=index)
            for index, value in enumerate(_sequence(document.get("servers")))
        ),
        paths=_path_items(_mapping(document.get("paths")), owner="paths"),
        webhooks=_path_items(_mapping(document.get("webhooks")), owner="webhooks"),
        components=_components(_mapping(document.get("components"))),
        security=tuple(
            freeze_source_map(_mapping(value))
            for value in _sequence(document.get("security"))
        ),
        tags=tuple(
            _tag(_mapping(value), index=index)
            for index, value in enumerate(_sequence(document.get("tags")))
        ),
        external_docs=_external_docs(
            _mapping(document.get("externalDocs")),
            source_path="$.externalDocs",
        ),
    )


def _info(raw: Mapping[str, Any]) -> NormalizedInfoContract:
    path = "$.info"
    contact_raw = _mapping(raw.get("contact"))
    license_raw = _mapping(raw.get("license"))
    return NormalizedInfoContract(
        source=source_object(
            raw,
            source_path=path,
            known_keys={
                "title",
                "summary",
                "description",
                "termsOfService",
                "contact",
                "license",
                "version",
            },
        ),
        title=presence_from_mapping(raw, "title", source_path=path),
        summary=presence_from_mapping(raw, "summary", source_path=path),
        description=presence_from_mapping(raw, "description", source_path=path),
        terms_of_service=presence_from_mapping(raw, "termsOfService", source_path=path),
        contact=NormalizedContactContract(
            source=source_object(
                contact_raw,
                source_path=f"{path}.contact",
                known_keys={"name", "url", "email"},
            ),
            name=presence_from_mapping(contact_raw, "name", source_path=f"{path}.contact"),
            url=presence_from_mapping(contact_raw, "url", source_path=f"{path}.contact"),
            email=presence_from_mapping(contact_raw, "email", source_path=f"{path}.contact"),
        ),
        license=NormalizedLicenseContract(
            source=source_object(
                license_raw,
                source_path=f"{path}.license",
                known_keys={"name", "identifier", "url"},
            ),
            name=presence_from_mapping(license_raw, "name", source_path=f"{path}.license"),
            identifier=presence_from_mapping(
                license_raw,
                "identifier",
                source_path=f"{path}.license",
            ),
            url=presence_from_mapping(license_raw, "url", source_path=f"{path}.license"),
        ),
        version=presence_from_mapping(raw, "version", source_path=path),
    )


def _server(raw: Mapping[str, Any], *, index: int) -> NormalizedServerContract:
    path = f"$.servers.{index}"
    variables = _mapping(raw.get("variables"))
    return NormalizedServerContract(
        source=source_object(
            raw,
            source_path=path,
            known_keys={"url", "description", "variables"},
        ),
        url=presence_from_mapping(raw, "url", source_path=path),
        description=presence_from_mapping(raw, "description", source_path=path),
        variables=MappingProxyType(
            {
                str(name): _server_variable(str(name), _mapping(value), owner=path)
                for name, value in variables.items()
            }
        ),
    )


def _server_variable(
    name: str,
    raw: Mapping[str, Any],
    *,
    owner: str,
) -> NormalizedServerVariableContract:
    path = f"{owner}.variables.{name}"
    return NormalizedServerVariableContract(
        name=name,
        source=source_object(
            raw,
            source_path=path,
            known_keys={"default", "description", "enum"},
        ),
        default=presence_from_mapping(raw, "default", source_path=path),
        description=presence_from_mapping(raw, "description", source_path=path),
        enum=tuple(_sequence(raw.get("enum"))),
    )


def _path_items(
    values: Mapping[str, Any],
    *,
    owner: str,
) -> Mapping[str, NormalizedPathItemContract]:
    return MappingProxyType(
        {
            str(name): _path_item(str(name), _mapping(value), owner=owner)
            for name, value in values.items()
        }
    )


def _path_item(
    name: str,
    raw: Mapping[str, Any],
    *,
    owner: str,
) -> NormalizedPathItemContract:
    path = f"$.{owner}.{name}"
    operation_methods = {
        "get",
        "put",
        "post",
        "delete",
        "options",
        "head",
        "patch",
        "trace",
    }
    return NormalizedPathItemContract(
        name=name,
        source=source_object(
            raw,
            source_path=path,
            known_keys={
                "$ref",
                "summary",
                "description",
                "servers",
                "parameters",
                *operation_methods,
            },
        ),
        summary=presence_from_mapping(raw, "summary", source_path=path),
        description=presence_from_mapping(raw, "description", source_path=path),
        ref=presence_from_mapping(raw, "$ref", source_path=path),
        servers=tuple(
            _server(_mapping(value), index=index)
            for index, value in enumerate(_sequence(raw.get("servers")))
        ),
        parameters=tuple(
            freeze_source_map(_mapping(value))
            for value in _sequence(raw.get("parameters"))
        ),
        operations=MappingProxyType(
            {
                method: source_object(
                    _mapping(raw.get(method)),
                    source_path=f"{path}.{method}",
                    known_keys={
                        "tags",
                        "summary",
                        "description",
                        "externalDocs",
                        "operationId",
                        "parameters",
                        "requestBody",
                        "responses",
                        "callbacks",
                        "deprecated",
                        "security",
                        "servers",
                    },
                )
                for method in sorted(operation_methods)
                if method in raw
            }
        ),
    )


def _components(raw: Mapping[str, Any]) -> NormalizedComponentsContract:
    path = "$.components"

    def registry(key: str) -> Mapping[str, SourceObject]:
        values = _mapping(raw.get(key))
        return MappingProxyType(
            {
                str(name): source_object(
                    _mapping(value),
                    source_path=f"{path}.{key}.{name}",
                )
                for name, value in values.items()
            }
        )

    return NormalizedComponentsContract(
        source=source_object(
            raw,
            source_path=path,
            known_keys={
                "schemas",
                "responses",
                "parameters",
                "examples",
                "requestBodies",
                "headers",
                "securitySchemes",
                "links",
                "callbacks",
                "pathItems",
            },
        ),
        schemas=registry("schemas"),
        responses=registry("responses"),
        parameters=registry("parameters"),
        examples=registry("examples"),
        request_bodies=registry("requestBodies"),
        headers=registry("headers"),
        security_schemes=registry("securitySchemes"),
        links=registry("links"),
        callbacks=registry("callbacks"),
        path_items=registry("pathItems"),
    )


def _tag(raw: Mapping[str, Any], *, index: int) -> NormalizedTagContract:
    path = f"$.tags.{index}"
    return NormalizedTagContract(
        source=source_object(
            raw,
            source_path=path,
            known_keys={"name", "description", "externalDocs"},
        ),
        name=presence_from_mapping(raw, "name", source_path=path),
        description=presence_from_mapping(raw, "description", source_path=path),
        external_docs=_external_docs(
            _mapping(raw.get("externalDocs")),
            source_path=f"{path}.externalDocs",
        ),
    )


def _external_docs(
    raw: Mapping[str, Any],
    *,
    source_path: str,
) -> NormalizedExternalDocsContract:
    return NormalizedExternalDocsContract(
        source=source_object(
            raw,
            source_path=source_path,
            known_keys={"description", "url"},
        ),
        description=presence_from_mapping(raw, "description", source_path=source_path),
        url=presence_from_mapping(raw, "url", source_path=source_path),
    )


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _sequence(value: Any) -> Sequence[Any]:
    if isinstance(value, Sequence) and not isinstance(value, str | bytes | bytearray):
        return value
    return ()
