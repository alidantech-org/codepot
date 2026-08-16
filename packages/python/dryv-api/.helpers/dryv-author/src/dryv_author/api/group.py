from __future__ import annotations

from typing import TYPE_CHECKING, Mapping, cast

if TYPE_CHECKING:
    from .author import Author

from dryv_author.core import AuthorRef, Declaration, EventRef, FailureRef, GroupRef, OperationRef, PolicyRef, PresentationRef, PropertyRef, RefKind, SchemaRef, StorageRef, ValueSourceRef, ViewRef, WorkflowRef, declaration_id, slug
from dryv_author.features import EventDeclaration, FailureDeclaration, FieldOptions, GroupDeclaration, OperationDeclaration, PolicyDeclaration, PresentationDeclaration, ProjectionStep, PropertyDeclaration, SchemaDeclaration, SchemaDeclarationKind, StorageDeclaration, ValueSourceDeclaration, ViewDeclaration, WorkflowDeclaration
from dryv_author.features.schemas import fields_from_mapping


class GroupBuilder:
    def __init__(self, author: "Author", ref: GroupRef, path: tuple[str, ...]) -> None:
        self.author = author
        self.ref = ref
        self.path = path

    @property
    def id(self) -> str:
        return self.ref.declaration_id

    def group(self, name: str) -> GroupBuilder:
        identifier = declaration_id(self.id, RefKind.GROUP.value, name)
        payload = GroupDeclaration(self.ref, self.path + (slug(name),))
        ref = cast(GroupRef, self._register(identifier, name, RefKind.GROUP, payload))
        return GroupBuilder(self.author, ref, payload.path)

    def property(self, name: str, annotation: object, *, options: FieldOptions | None = None) -> PropertyRef[object]:
        return cast(PropertyRef[object], self._declare(name, RefKind.PROPERTY, PropertyDeclaration(annotation, options or FieldOptions())))

    def schema(self, name: str, fields: Mapping[str, object] | None = None, *, extends: SchemaRef[object] | None = None) -> SchemaRef[object]:
        return cast(SchemaRef[object], self._declare(name, RefKind.SCHEMA, SchemaDeclaration(SchemaDeclarationKind.OBJECT, fields=fields_from_mapping(dict(fields or {})), extends=extends)))

    def enum(self, name: str, *values: str) -> SchemaRef[object]:
        return cast(SchemaRef[object], self._declare(name, RefKind.SCHEMA, SchemaDeclaration(SchemaDeclarationKind.ENUM, enum_values=tuple(values))))

    def alias(self, name: str, annotation: object) -> SchemaRef[object]:
        return cast(SchemaRef[object], self._declare(name, RefKind.SCHEMA, SchemaDeclaration(SchemaDeclarationKind.ALIAS, alias_of=annotation)))

    def array_schema(self, name: str, item_type: object) -> SchemaRef[object]:
        return cast(SchemaRef[object], self._declare(name, RefKind.SCHEMA, SchemaDeclaration(SchemaDeclarationKind.ARRAY, item_type=item_type)))

    def project_schema(self, name: str, source: SchemaRef[object], *steps: ProjectionStep) -> SchemaRef[object]:
        return cast(SchemaRef[object], self._declare(name, RefKind.SCHEMA, SchemaDeclaration(SchemaDeclarationKind.OBJECT, source=source, projections=tuple(steps))))

    def failure(self, name: str, code: str, *, schema: SchemaRef[object] | None = None, message: str | None = None) -> FailureRef:
        return cast(FailureRef, self._declare(name, RefKind.FAILURE, FailureDeclaration(code, schema, message)))

    def event(self, name: str, declaration: EventDeclaration | None = None) -> EventRef[object]:
        return cast(EventRef[object], self._declare(name, RefKind.EVENT, declaration or EventDeclaration()))

    def policy(self, name: str, declaration: PolicyDeclaration | None = None) -> PolicyRef:
        return cast(PolicyRef, self._declare(name, RefKind.POLICY, declaration or PolicyDeclaration()))

    def operation(self, name: str, declaration: OperationDeclaration | None = None) -> OperationRef[object, object]:
        return cast(OperationRef[object, object], self._declare(name, RefKind.OPERATION, declaration or OperationDeclaration()))

    def storage(self, name: str, declaration: StorageDeclaration) -> StorageRef[object]:
        return cast(StorageRef[object], self._declare(name, RefKind.STORAGE, declaration))

    def source(self, name: str, declaration: ValueSourceDeclaration) -> ValueSourceRef[object]:
        return cast(ValueSourceRef[object], self._declare(name, RefKind.VALUE_SOURCE, declaration))

    def view(self, name: str, declaration: ViewDeclaration | None = None) -> ViewRef:
        return cast(ViewRef, self._declare(name, RefKind.VIEW, declaration or ViewDeclaration()))

    def workflow(self, name: str, declaration: WorkflowDeclaration) -> WorkflowRef:
        return cast(WorkflowRef, self._declare(name, RefKind.WORKFLOW, declaration))

    def presentation(self, name: str, declaration: PresentationDeclaration) -> PresentationRef:
        return cast(PresentationRef, self._declare(name, RefKind.PRESENTATION, declaration))

    def _declare(self, name: str, kind: RefKind, payload: object) -> AuthorRef[object]:
        return self._register(declaration_id(self.id, kind.value, name), name, kind, payload)

    def _register(self, identifier: str, name: str, kind: RefKind, payload: object) -> AuthorRef[object]:
        declaration = Declaration(identifier, name, kind, self.id, payload, self.author.metadata.source)
        return self.author.registry.register(declaration)


__all__ = ["GroupBuilder"]
