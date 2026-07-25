"""Root compiled Codepot IR document model."""

from __future__ import annotations

from archives.codepot.src.spec.ir.properties.definition import PropertiesDefinition
from archives.codepot.src.spec.ir.resource.definition import ResourceDefinition
from archives.codepot.src.spec.ir.response.definition import ResponsesDefinition
from archives.codepot.src.spec.ir.schema.definition import SchemasDefinition
from archives.codepot.src.spec.ir.security.definition import SecurityDefinition
from archives.codepot.src.spec.ir.shared.base import DefinitionItem
from archives.codepot.src.spec.ir.shared.content import ContentTypeDefinition
from archives.codepot.src.spec.ir.shared.info import InfoDefinition
from archives.codepot.src.spec.ir.shared.url import UrlDefinition
from pydantic import ConfigDict


class CodepotDefinition(DefinitionItem):
    """Stable compiled Codepot IR document consumed by codegen."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    codepot: str
    key: str
    version: int

    info: InfoDefinition
    urls: list[UrlDefinition]

    content_types: dict[str, ContentTypeDefinition]
    properties: PropertiesDefinition
    schemas: SchemasDefinition
    responses: ResponsesDefinition
    security: SecurityDefinition
    resources: dict[str, ResourceDefinition]
