from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Mapping, cast
from uuid import uuid4

from .declarations import Declaration
from .diagnostics import (
    AUTHOR_CORE_UNSUPPORTED,
    AuthorDiagnostic,
    AuthorDiagnostics,
    AuthorDiagnosticSeverity,
)
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
    WorkflowStepRef,
)
from .schemas import (
    FieldOptions,
    ProjectionStep,
    PropertyDeclaration,
    SchemaDeclaration,
    SchemaDeclarationKind,
    fields_from_mapping,
)


def _new_author_id() -> str:
    return f"author-{uuid4().hex}"


_REF_TYPES: dict[RefKind, type[Ref[object]]] = {
    RefKind.GROUP: GroupRef,
    RefKind.PROPERTY: PropertyRef,
    RefKind.SCHEMA: SchemaRef,
    RefKind.OPERATION: OperationRef,
    RefKind.EVENT: EventRef,
    RefKind.POLICY: PolicyRef,
    RefKind.STORAGE: StorageRef,
    RefKind.VIEW: ViewRef,
    RefKind.WORKFLOW: WorkflowRef,
    RefKind.WORKFLOW_STEP: WorkflowStepRef,
}

_UNSUPPORTED_CORE_KINDS = frozenset({RefKind.VALUE_SOURCE, RefKind.PRESENTATION})


@dataclass(slots=True)
class Author:
    name: str
    version: str | None = None
    options: AuthorOptions = field(default_factory=AuthorOptions)
    _author_id: str = field(default_factory=_new_author_id, init=False, repr=False)
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

    def declaration(self, ref: Ref[object]) -> Declaration:
        self._require_local(ref)
        return self._declarations[ref.declaration_id]

    def declare(
        self,
        kind: RefKind,
        name: str,
        *,
        declaration_id: str | None = None,
        payload: object | None = None,
    ) -> Ref[object]:
        if self._frozen:
            raise RuntimeError("author session is frozen")
        if kind in _UNSUPPORTED_CORE_KINDS:
            self._reject_unsupported(kind, name)
        if kind not in _REF_TYPES:
            raise ValueError(f"unsupported author ref kind: {kind.value}")
        if len(self._declarations) >= self.options.max_declarations:
            raise RuntimeError("author declaration limit exceeded")
        normalized_id = declaration_id or self._default_id(kind, name)
        if normalized_id in self._declarations:
            raise ValueError(f"duplicate declaration id: {normalized_id}")
        declaration = Declaration(normalized_id, name, kind, payload=payload)
        self._declarations[normalized_id] = declaration
        return _REF_TYPES[kind](RefIdentity(self._author_id, normalized_id, kind))

    def group(self, name: str, *, declaration_id: str | None = None) -> GroupRef:
        return cast(GroupRef, self.declare(RefKind.GROUP, name, declaration_id=declaration_id))

    def property(
        self,
        name: str,
        annotation: object,
        *,
        declaration_id: str | None = None,
        **options: object,
    ) -> PropertyRef[object]:
        payload = PropertyDeclaration(annotation, FieldOptions(**options))  # type: ignore[arg-type]
        return cast(
            PropertyRef[object],
            self.declare(RefKind.PROPERTY, name, declaration_id=declaration_id, payload=payload),
        )

    def schema(
        self,
        name: str,
        fields: Mapping[str, object] | None = None,
        *,
        declaration_id: str | None = None,
    ) -> SchemaRef[object]:
        payload = SchemaDeclaration(
            SchemaDeclarationKind.OBJECT,
            fields=fields_from_mapping(fields or {}),
        )
        return cast(
            SchemaRef[object],
            self.declare(RefKind.SCHEMA, name, declaration_id=declaration_id, payload=payload),
        )

    def enum_schema(
        self,
        name: str,
        values: type[Enum] | tuple[str, ...],
        *,
        declaration_id: str | None = None,
    ) -> SchemaRef[object]:
        enum_values = (
            tuple(str(item.value) for item in values)
            if isinstance(values, type) and issubclass(values, Enum)
            else tuple(values)
        )
        payload = SchemaDeclaration(SchemaDeclarationKind.ENUM, enum_values=enum_values)
        return cast(
            SchemaRef[object],
            self.declare(RefKind.SCHEMA, name, declaration_id=declaration_id, payload=payload),
        )

    def project_schema(
        self,
        source: SchemaRef[object],
        name: str,
        *steps: ProjectionStep,
        declaration_id: str | None = None,
    ) -> SchemaRef[object]:
        self._require_local(source, RefKind.SCHEMA)
        payload = SchemaDeclaration(
            SchemaDeclarationKind.OBJECT,
            source_schema=source,
            projection_steps=steps,
        )
        return cast(
            SchemaRef[object],
            self.declare(RefKind.SCHEMA, name, declaration_id=declaration_id, payload=payload),
        )

    def operation(
        self,
        name: str,
        *,
        declaration_id: str | None = None,
    ) -> OperationRef[object, object]:
        return cast(
            OperationRef[object, object],
            self.declare(RefKind.OPERATION, name, declaration_id=declaration_id),
        )

    def event(self, name: str, *, declaration_id: str | None = None) -> EventRef[object]:
        return cast(EventRef[object], self.declare(RefKind.EVENT, name, declaration_id=declaration_id))

    def policy(self, name: str, *, declaration_id: str | None = None) -> PolicyRef:
        return cast(PolicyRef, self.declare(RefKind.POLICY, name, declaration_id=declaration_id))

    def storage(self, name: str, *, declaration_id: str | None = None) -> StorageRef[object]:
        return cast(StorageRef[object], self.declare(RefKind.STORAGE, name, declaration_id=declaration_id))

    def view(self, name: str, *, declaration_id: str | None = None) -> ViewRef:
        return cast(ViewRef, self.declare(RefKind.VIEW, name, declaration_id=declaration_id))

    def workflow(self, name: str, *, declaration_id: str | None = None) -> WorkflowRef:
        return cast(WorkflowRef, self.declare(RefKind.WORKFLOW, name, declaration_id=declaration_id))

    def _require_local(self, ref: Ref[object], kind: RefKind | None = None) -> None:
        if ref.identity.author_id != self._author_id:
            raise ValueError("foreign author-session ref")
        if kind is not None and ref.kind is not kind:
            raise TypeError(f"expected {kind.value} ref, received {ref.kind.value}")
        if ref.declaration_id not in self._declarations:
            raise ValueError("unknown declaration ref")

    def _reject_unsupported(self, kind: RefKind, name: str) -> None:
        diagnostic = AuthorDiagnostic(
            code=AUTHOR_CORE_UNSUPPORTED,
            severity=AuthorDiagnosticSeverity.ERROR,
            message=f"core IR does not support author declaration kind '{kind.value}'",
            details=(("kind", kind.value), ("name", name)),
        )
        self._diagnostics = self._diagnostics.add(diagnostic)
        raise ValueError(f"{AUTHOR_CORE_UNSUPPORTED}: {kind.value}")

    def _default_id(self, kind: RefKind, name: str) -> str:
        token = "-".join(part.lower() for part in name.replace("_", " ").split())
        return self.options.id_separator.join((kind.value, token))
