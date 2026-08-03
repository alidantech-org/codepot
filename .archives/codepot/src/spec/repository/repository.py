"""Public SpecRepository facade."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from archives.codepot.src.contracts.spec.context import SpecContext, SpecCounts, SpecMetadata
from archives.codepot.src.contracts.spec.dependencies import SpecDependency
from archives.codepot.src.contracts.spec.records import SpecRecord
from archives.codepot.src.contracts.spec.refs import SpecRef
from archives.codepot.src.spec.ir.properties.composite.definition import CompositeDefinition
from archives.codepot.src.spec.ir.properties.enum.definition import EnumDefinition
from archives.codepot.src.spec.ir.properties.primitive.definition import PrimitiveDefinition
from archives.codepot.src.spec.ir.resource.definition import ResourceDefinition
from archives.codepot.src.spec.ir.schema.dto.definition import DtoDefinition
from archives.codepot.src.spec.ir.schema.entity.definition import EntityDefinition
from archives.codepot.src.spec.ir.schema.model.definition import ModelDefinition
from archives.codepot.src.spec.ir.shared.content import ContentTypeDefinition
from archives.codepot.src.spec.ir.shared.url import UrlDefinition
from archives.codepot.src.spec.loader import load_spec
from archives.codepot.src.spec.repository.context import build_context
from archives.codepot.src.spec.repository.dependencies import dependencies_for
from archives.codepot.src.spec.repository.indexes import SpecRepositoryIndexes, build_indexes
from archives.codepot.src.spec.repository.record_sets import SpecRecordQuery
from archives.codepot.src.spec.utils.enums import SpecSubject


@dataclass(frozen=True)
class SpecRepository:
    """Typed read-only repository over a compiled Codepot spec."""

    context: SpecContext
    indexes: SpecRepositoryIndexes

    @classmethod
    def from_file(cls, path: Path) -> SpecRepository:
        """Load a compiled spec file and build a repository."""

        document = load_spec(path)
        context = build_context(path, document)
        indexes = build_indexes(context.all_records)

        return cls(context=context, indexes=indexes)

    def get_context(self) -> SpecContext:
        """Return normalized spec context."""

        return self.context

    def get_counts(self) -> SpecCounts:
        """Return normalized spec counts."""

        return self.context.counts

    def get_metadata(self) -> SpecMetadata:
        """Return normalized spec metadata."""

        return self.context.metadata

    def records_for(self, subject: SpecSubject) -> tuple[SpecRecord[object], ...]:
        """Return normalized records for a subject."""

        return self.indexes.records_for_subject(subject.value)

    def resolve(self, ref: SpecRef) -> SpecRecord[object] | None:
        """Resolve a normalized spec ref."""

        return self.indexes.resolve(ref)

    def dependencies_for(
        self,
        record: SpecRecord[object],
    ) -> tuple[SpecDependency, ...]:
        """Return normalized dependencies for a record."""

        return dependencies_for(record)

    def urls(self) -> SpecRecordQuery[UrlDefinition]:
        """Return URL records."""

        return SpecRecordQuery(
            subject=SpecSubject.URLS, records=self.context.urls.items
        )

    def content_types(self) -> SpecRecordQuery[ContentTypeDefinition]:
        """Return content type records."""

        return SpecRecordQuery(
            subject=SpecSubject.CONTENT_TYPES,
            records=self.context.content_types.items,
        )

    def primitives(self) -> SpecRecordQuery[PrimitiveDefinition]:
        """Return primitive records."""

        return SpecRecordQuery(
            subject=SpecSubject.PRIMITIVES,
            records=self.context.primitives.items,
        )

    def enums(self) -> SpecRecordQuery[EnumDefinition]:
        """Return enum records."""

        return SpecRecordQuery(
            subject=SpecSubject.ENUMS, records=self.context.enums.items
        )

    def composites(self) -> SpecRecordQuery[CompositeDefinition]:
        """Return composite records."""

        return SpecRecordQuery(
            subject=SpecSubject.COMPOSITES,
            records=self.context.composites.items,
        )

    def entities(self) -> SpecRecordQuery[EntityDefinition]:
        """Return entity records."""

        return SpecRecordQuery(
            subject=SpecSubject.ENTITIES,
            records=self.context.entities.items,
        )

    def models(self) -> SpecRecordQuery[ModelDefinition]:
        """Return model records."""

        return SpecRecordQuery(
            subject=SpecSubject.MODELS, records=self.context.models.items
        )

    def dtos(self) -> SpecRecordQuery[DtoDefinition]:
        """Return DTO records."""

        return SpecRecordQuery(
            subject=SpecSubject.DTOS, records=self.context.dtos.items
        )

    def resources(self) -> SpecRecordQuery[ResourceDefinition]:
        """Return resource records."""

        return SpecRecordQuery(
            subject=SpecSubject.RESOURCES,
            records=self.context.resources.items,
        )
