from __future__ import annotations

from dataclasses import dataclass, field
from itertools import count
from threading import Lock
from typing import cast

from .declarations import Declaration
from .options import AuthorOptions
from .refs import (
    EventRef,
    GroupRef,
    OperationRef,
    PolicyRef,
    PresentationRef,
    PropertyRef,
    Ref,
    RefIdentity,
    RefKind,
    SchemaRef,
    StorageRef,
    ValueSourceRef,
    ViewRef,
    WorkflowRef,
    WorkflowStepRef,
)

_AUTHOR_COUNTER = count(1)
_AUTHOR_COUNTER_LOCK = Lock()


def _next_author_id() -> str:
    with _AUTHOR_COUNTER_LOCK:
        return f"author-{next(_AUTHOR_COUNTER)}"


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
    RefKind.VALUE_SOURCE: ValueSourceRef,
    RefKind.PRESENTATION: PresentationRef,
}


@dataclass(slots=True)
class Author:
    name: str
    version: str | None = None
    options: AuthorOptions = field(default_factory=AuthorOptions)
    _author_id: str = field(default_factory=_next_author_id, init=False, repr=False)
    _declarations: dict[str, Declaration] = field(default_factory=dict, init=False, repr=False)
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
    def declarations(self) -> tuple[Declaration, ...]:
        return tuple(sorted(self._declarations.values(), key=lambda item: (item.kind.value, item.id)))

    def freeze(self) -> None:
        self._frozen = True

    def declare(self, kind: RefKind, name: str, *, declaration_id: str | None = None) -> Ref[object]:
        if self._frozen:
            raise RuntimeError("author session is frozen")
        if len(self._declarations) >= self.options.max_declarations:
            raise RuntimeError("author declaration limit exceeded")
        normalized_id = declaration_id or self._default_id(kind, name)
        if normalized_id in self._declarations:
            raise ValueError(f"duplicate declaration id: {normalized_id}")
        declaration = Declaration(normalized_id, name, kind)
        self._declarations[normalized_id] = declaration
        ref_type = _REF_TYPES[kind]
        return ref_type(RefIdentity(self._author_id, normalized_id, kind))

    def group(self, name: str, *, declaration_id: str | None = None) -> GroupRef:
        return cast(GroupRef, self.declare(RefKind.GROUP, name, declaration_id=declaration_id))

    def schema(self, name: str, *, declaration_id: str | None = None) -> SchemaRef[object]:
        return cast(SchemaRef[object], self.declare(RefKind.SCHEMA, name, declaration_id=declaration_id))

    def property(self, name: str, *, declaration_id: str | None = None) -> PropertyRef[object]:
        return cast(PropertyRef[object], self.declare(RefKind.PROPERTY, name, declaration_id=declaration_id))

    def operation(self, name: str, *, declaration_id: str | None = None) -> OperationRef[object, object]:
        return cast(OperationRef[object, object], self.declare(RefKind.OPERATION, name, declaration_id=declaration_id))

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

    def _default_id(self, kind: RefKind, name: str) -> str:
        token = "-".join(part.lower() for part in name.replace("_", " ").split())
        return self.options.id_separator.join((kind.value, token))
