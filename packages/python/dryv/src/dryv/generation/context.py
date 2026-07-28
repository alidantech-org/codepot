from __future__ import annotations

from dataclasses import dataclass, field

from dryv.config import PackManifest, ProjectConfig
from dryv.domain.generation import SelectionContext
from dryv.domain.ir import (
    Contract,
    Event,
    Operation,
    Presentation,
    PresentationEntry,
    Schema,
    SemanticId,
    StorageMapping,
    ValueSource,
    View,
)
from dryv.domain.ir.validation import SemanticIndex

from .models import ArtifactPlan, ModuleCollection, ModuleDescriptor

SafeRecordValue = object
SafeRecord = tuple[tuple[str, SafeRecordValue], ...]


@dataclass(slots=True)
class RenderContextBuilder:
    contract: Contract
    _index: SemanticIndex = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._index, _ = SemanticIndex.build(self.contract)

    def build(
        self,
        *,
        selection: SelectionContext | None,
        project: ProjectConfig,
        manifest: PackManifest,
        artifact: ArtifactPlan,
        options: tuple[tuple[str, object], ...],
        bindings: tuple[tuple[str, object], ...],
    ) -> tuple[tuple[str, object], ...]:
        roots: dict[str, object] = {
            "artifact": _record(
                id=artifact.id,
                path=artifact.output_path,
                selection_key=artifact.selection_key,
                semantic_id=artifact.semantic_id,
                template_id=artifact.template_id,
            ),
            "bindings": bindings,
            "contract": self.contract,
            "exports": _module_mapping(artifact.exports),
            "imports": _module_mapping(artifact.imports),
            "options": options,
            "pack": _record(id=manifest.id, version=manifest.version),
            "project": _record(name=project.name),
            "target": _record(id=artifact.target_id),
        }
        if selection is not None:
            if selection.group is not None:
                roots["group"] = selection.group
            if selection.schema is not None:
                roots["schema"] = selection.schema
            if selection.operation is not None:
                roots["operation"] = self._operation(selection.operation)
            if selection.view is not None:
                roots["view"] = self._view(selection.view)
            if selection.storage_mapping is not None:
                roots["mapping"] = self._mapping(selection.storage_mapping)
            if selection.workflow is not None:
                roots["workflow"] = selection.workflow
            if selection.policy is not None:
                roots["policy"] = selection.policy
            if selection.event is not None:
                roots["event"] = self._event(selection.event)
            if selection.value_source is not None:
                roots["value_source"] = self._value_source(selection.value_source)
            if selection.presentation is not None:
                roots["presentation"] = self._presentation(selection.presentation)
            if selection.presentation_entry is not None:
                roots["entry"] = self._presentation_entry(selection.presentation_entry)
        return tuple(sorted(roots.items()))

    def _operation(self, operation: Operation) -> SafeRecord:
        inputs = tuple(
            _record(
                data=item.data,
                name=item.name,
                nullable=item.nullable,
                readonly=item.readonly,
                required=item.required,
                schema=self._schema(item.schema),
            )
            for item in operation.inputs
        )
        outputs = tuple(
            _record(
                data=item.data,
                name=item.name,
                optional=item.optional,
                schema=self._schema(item.schema),
            )
            for item in operation.outputs
        )
        failures = tuple(
            _record(
                code=item.code,
                data=item.data,
                message=item.message,
                schema=self._schema(item.schema),
            )
            for item in operation.failures
        )
        return _record(
            data=operation.data,
            effects=operation.effects,
            facets=operation.facets,
            failures=failures,
            id=operation.id,
            inputs=inputs,
            name=operation.name,
            outputs=outputs,
        )

    def _mapping(self, mapping: StorageMapping) -> SafeRecord:
        schema = self._schema(mapping.schema)
        fields = tuple(
            _record(
                column=item.column,
                column_type=item.column_type,
                field=self._field(item.field),
                indexed=item.indexed,
                nullable=item.nullable,
                unique=item.unique,
            )
            for item in mapping.fields
        )
        return _record(
            data=mapping.data,
            fields=fields,
            id=mapping.id,
            indexes=tuple(
                tuple(self._field(field_id) for field_id in index_fields)
                for index_fields in mapping.indexes
            ),
            name=mapping.name,
            primary_key=tuple(self._field(field_id) for field_id in mapping.primary_key),
            schema=schema,
            source=mapping.source,
        )

    def _view(self, view: View) -> SafeRecord:
        return _record(
            access=view.access,
            data=view.data,
            id=view.id,
            name=view.name,
            parts=tuple(self._view(item) for item in view.parts),
            schema=self._schema(view.schema),
            triggers=tuple(
                _record(
                    interaction=item.interaction,
                    name=item.name,
                    operation=self._index.operations.get(item.operation),
                    payload_schema=self._schema(item.payload_schema),
                )
                for item in view.triggers
            ),
        )

    def _event(self, event: Event) -> SafeRecord:
        return _record(
            context_schema=self._schema(event.context_schema),
            data=event.data,
            id=event.id,
            name=event.name,
            payload_schema=self._schema(event.payload_schema),
            source=event.source,
            version=event.version,
        )

    def _value_source(self, source: ValueSource) -> SafeRecord:
        return _record(
            data=source.data,
            id=source.id,
            label_fields=tuple(self._field(item) for item in source.label_fields),
            name=source.name,
            operation=self._index.operations.get(source.operation),
            output=source.output,
            search_input=source.search_input,
            value_field=self._field(source.value_field),
        )

    def _presentation(self, presentation: Presentation) -> SafeRecord:
        return _record(
            channel=presentation.channel,
            data=presentation.data,
            entries=tuple(self._presentation_entry(item) for item in presentation.entries),
            id=presentation.id,
            name=presentation.name,
        )

    def _presentation_entry(self, entry: PresentationEntry) -> SafeRecord:
        return _record(
            address=entry.address,
            data=entry.data,
            id=entry.id,
            name=entry.name,
            navigation_parent=entry.navigation_parent,
            order=entry.order,
            view=self._index.views.get(entry.view),
        )

    def _schema(self, semantic_id: SemanticId | None) -> Schema | None:
        return self._index.schemas.get(semantic_id) if semantic_id is not None else None

    def _field(self, semantic_id: SemanticId) -> object:
        return self._index.fields.get(semantic_id, semantic_id)


def _module_mapping(
    values: tuple[tuple[str, ModuleCollection], ...],
) -> SafeRecord:
    return tuple(
        (
            key,
            _record(
                modules=tuple(_module(item) for item in collection.modules),
            ),
        )
        for key, collection in values
    )


def _module(value: ModuleDescriptor) -> SafeRecord:
    return _record(
        artifact_path=value.artifact_path,
        selection_key=value.selection_key,
        semantic_id=value.semantic_id,
        specifier=value.specifier,
        symbols=value.symbols,
    )


def _record(**values: object) -> SafeRecord:
    return tuple(sorted(values.items()))
