from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, cast
from uuid import uuid4

from .declarations import Declaration
from .diagnostics import AUTHOR_CORE_UNSUPPORTED, AuthorDiagnostic, AuthorDiagnostics
from .options import AuthorOptions
from .refs import (
    EventRef,
    GroupRef,
    OperationRef,
    PolicyRef,
    PropertyRef,
    Ref,
    RefIdentity,
    RefKind,
    SchemaRef,
    StorageRef,
    ViewRef,
    WorkflowRef,
)
from .schemas import FieldOptions, ProjectionStep, PropertyDeclaration, SchemaDeclaration, SchemaDeclarationKind, fields_from_mapping
from .semantics import EventDeclaration, OperationDeclaration, PolicyDeclaration, StorageDeclaration, ViewDeclaration, WorkflowDeclaration

_REF_TYPES: dict[RefKind, type[Ref[Any]]] = {
    RefKind.GROUP: GroupRef,
    RefKind.PROPERTY: PropertyRef,
    RefKind.SCHEMA: SchemaRef,
    RefKind.OPERATION: OperationRef,
    RefKind.EVENT: EventRef,
    RefKind.POLICY: PolicyRef,
    RefKind.STORAGE: StorageRef,
    RefKind.VIEW: ViewRef,
    RefKind.WORKFLOW: WorkflowRef,
}
_UNSUPPORTED_KINDS = {RefKind.VALUE_SOURCE, RefKind.PRESENTATION}


@dataclass(slots=True)
class Author:
    name: str
    version: str | None = None
    options: AuthorOptions = field(default_factory=AuthorOptions)
    _author_id: str = field(default_factory=lambda: f"author-{uuid4()}", init=False, repr=False)
    _declarations: dict[str, Declaration] = field(default_factory=dict, init=False, repr=False)
    _diagnostics: AuthorDiagnostics = field(default_factory=AuthorDiagnostics, init=False, repr=False)
    _frozen: bool = field(default=False, init=False, repr=False)

    def __post_init__(self) -> None:
        if not self.name or self.name.strip() != self.name:
            raise ValueError("author name must be a non-empty trimmed string")

    @property
    def author_id(self) -> str:
        return self._author_id

    @property
    def frozen(self) -> bool:
        return self._frozen

    @property
    def diagnostics(self) -> AuthorDiagnostics:
        return self._diagnostics

    @property
    def declarations(self) -> tuple[Declaration, ...]:
        return tuple(sorted(self._declarations.values(), key=lambda item: (item.kind.value, item.id)))

    def freeze(self) -> None:
        self._frozen = True

    def declaration(self, ref: Ref[Any]) -> Declaration:
        self._require_local(ref)
        return self._declarations[ref.declaration_id]

    def declare(
        self,
        kind: RefKind,
        name: str,
        *,
        declaration_id: str | None = None,
        group: GroupRef | None = None,
        payload: object | None = None,
    ) -> Ref[Any]:
        if kind in _UNSUPPORTED_KINDS:
            diagnostic = AuthorDiagnostic(
                AUTHOR_CORE_UNSUPPORTED,
                f"{kind.value} is not supported by the public core IR",
                details=(("kind", kind.value),),
            )
            self._diagnostics = self._diagnostics.add(diagnostic)
            if self.options.unsupported_core.value == "error":
                raise ValueError(diagnostic.message)
            raise ValueError(f"{AUTHOR_CORE_UNSUPPORTED}: {diagnostic.message}")
        if self._frozen:
            raise RuntimeError("author session is frozen")
        if len(self._declarations) >= self.options.max_declarations:
            raise RuntimeError("author declaration limit exceeded")
        if group is not None:
            self._require_local(group, RefKind.GROUP)
        normalized_id = declaration_id or self._default_id(kind, name)
        if normalized_id in self._declarations:
            raise ValueError(f"duplicate declaration id: {normalized_id}")
        self._declarations[normalized_id] = Declaration(
            normalized_id,
            name,
            kind,
            group_id=group.declaration_id if group else None,
            payload=payload,
        )
        return _REF_TYPES[kind](RefIdentity(self._author_id, normalized_id, kind))

    def _replace_payload(self, ref: Ref[Any], payload: object) -> None:
        self._require_local(ref)
        current = self._declarations[ref.declaration_id]
        self._declarations[ref.declaration_id] = Declaration(
            current.id, current.name, current.kind, current.group_id, payload
        )

    def group(self, name: str, *, declaration_id: str | None = None) -> GroupRef:
        return cast(GroupRef, self.declare(RefKind.GROUP, name, declaration_id=declaration_id))

    def property(
        self,
        name: str,
        annotation: object,
        *,
        options: FieldOptions | None = None,
        declaration_id: str | None = None,
        group: GroupRef | None = None,
    ) -> PropertyRef[object]:
        payload = PropertyDeclaration(annotation, options or FieldOptions())
        return cast(PropertyRef[object], self.declare(RefKind.PROPERTY, name, declaration_id=declaration_id, group=group, payload=payload))

    def schema(
        self,
        name: str,
        fields: Mapping[str, object] | None = None,
        *,
        declaration_id: str | None = None,
        group: GroupRef | None = None,
    ) -> SchemaRef[object]:
        payload = SchemaDeclaration(SchemaDeclarationKind.OBJECT, fields=fields_from_mapping(fields or {}))
        return cast(SchemaRef[object], self.declare(RefKind.SCHEMA, name, declaration_id=declaration_id, group=group, payload=payload))

    def enum_schema(
        self,
        name: str,
        values: type[Enum] | tuple[str, ...],
        *,
        declaration_id: str | None = None,
        group: GroupRef | None = None,
    ) -> SchemaRef[object]:
        if isinstance(values, type) and issubclass(values, Enum):
            raw_values = tuple(item.value for item in values)
            if any(not isinstance(value, str) for value in raw_values):
                raise TypeError("public core enum values must be strings")
            enum_values = cast(tuple[str, ...], raw_values)
        else:
            enum_values = values
        payload = SchemaDeclaration(SchemaDeclarationKind.ENUM, enum_values=enum_values)
        return cast(SchemaRef[object], self.declare(RefKind.SCHEMA, name, declaration_id=declaration_id, group=group, payload=payload))

    def project_schema(self, source: SchemaRef[object], name: str, *steps: ProjectionStep, declaration_id: str | None = None, group: GroupRef | None = None) -> SchemaRef[object]:
        self._require_local(source, RefKind.SCHEMA)
        payload = SchemaDeclaration(SchemaDeclarationKind.OBJECT, source_schema=source, projection_steps=steps)
        return cast(SchemaRef[object], self.declare(RefKind.SCHEMA, name, declaration_id=declaration_id, group=group, payload=payload))

    def operation(self, name: str, declaration: OperationDeclaration | None = None, *, declaration_id: str | None = None, group: GroupRef | None = None) -> OperationRef[object, object]:
        return cast(OperationRef[object, object], self.declare(RefKind.OPERATION, name, declaration_id=declaration_id, group=group, payload=declaration or OperationDeclaration()))

    def event(self, name: str, declaration: EventDeclaration | None = None, *, declaration_id: str | None = None, group: GroupRef | None = None) -> EventRef[object]:
        return cast(EventRef[object], self.declare(RefKind.EVENT, name, declaration_id=declaration_id, group=group, payload=declaration or EventDeclaration()))

    def policy(self, name: str, declaration: PolicyDeclaration | None = None, *, declaration_id: str | None = None, group: GroupRef | None = None) -> PolicyRef:
        return cast(PolicyRef, self.declare(RefKind.POLICY, name, declaration_id=declaration_id, group=group, payload=declaration or PolicyDeclaration()))

    def storage(self, name: str, declaration: StorageDeclaration, *, declaration_id: str | None = None, group: GroupRef | None = None) -> StorageRef[object]:
        self._require_local(declaration.schema, RefKind.SCHEMA)
        return cast(StorageRef[object], self.declare(RefKind.STORAGE, name, declaration_id=declaration_id, group=group, payload=declaration))

    def view(self, name: str, declaration: ViewDeclaration | None = None, *, declaration_id: str | None = None, group: GroupRef | None = None) -> ViewRef:
        return cast(ViewRef, self.declare(RefKind.VIEW, name, declaration_id=declaration_id, group=group, payload=declaration or ViewDeclaration()))

    def workflow(self, name: str, declaration: WorkflowDeclaration | None = None, *, declaration_id: str | None = None, group: GroupRef | None = None) -> WorkflowRef:
        return cast(WorkflowRef, self.declare(RefKind.WORKFLOW, name, declaration_id=declaration_id, group=group, payload=declaration or WorkflowDeclaration()))

    def pydantic_model(self, model: type[object], *, name: str | None = None, group: GroupRef | None = None) -> SchemaRef[object]:
        from .pydantic import PydanticCompiler
        return PydanticCompiler(self, group=group).compile(model, name=name)

    def compile(self) -> object:
        from .compiler import compile_author
        return compile_author(self)

    def _require_local(self, ref: Ref[Any], kind: RefKind | None = None) -> None:
        if ref.identity.author_id != self._author_id:
            raise ValueError("foreign author-session ref")
        if kind is not None and ref.kind is not kind:
            raise TypeError(f"expected {kind.value} ref, received {ref.kind.value}")
        if ref.declaration_id not in self._declarations:
            raise ValueError("unknown declaration ref")

    def _default_id(self, kind: RefKind, name: str) -> str:
        token = "-".join(part.lower() for part in name.replace("_", " ").split())
        return self.options.id_separator.join((kind.value, token))
