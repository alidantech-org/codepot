from __future__ import annotations

from typing import Mapping, cast

from dryv_author.compiler import AuthoringResult, compile_author
from dryv_author.core import AuthorMetadata, AuthorSource, Declaration, DeclarationRegistry, GroupRef, RefKind
from dryv_author.features import EventDeclaration, FieldOptions, GroupDeclaration, OperationDeclaration, PolicyDeclaration, PresentationDeclaration, ProjectionStep, StorageDeclaration, ValueSourceDeclaration, ViewDeclaration, WorkflowDeclaration

from .group import GroupBuilder


class Author:
    def __init__(self, name: str, *, version: str | None = None, source_id: str | None = None) -> None:
        source = AuthorSource(source_id) if source_id else None
        self.metadata = AuthorMetadata(name, version, source)
        self.registry = DeclarationRegistry(self.metadata.key)
        root_declaration = Declaration("group/root", name, RefKind.GROUP, "group/root", GroupDeclaration(None, ()), source)
        root_ref = cast(GroupRef, self.registry.register(root_declaration))
        self.root = GroupBuilder(self, root_ref, ())

    @property
    def name(self) -> str:
        return self.metadata.name

    @property
    def version(self) -> str | None:
        return self.metadata.version

    def group(self, name: str) -> GroupBuilder:
        return self.root.group(name)

    def property(self, name: str, annotation: object, *, options: FieldOptions | None = None):
        return self.root.property(name, annotation, options=options)

    def schema(self, name: str, fields: Mapping[str, object] | None = None, *, extends=None):
        return self.root.schema(name, fields, extends=extends)

    def enum(self, name: str, *values: str):
        return self.root.enum(name, *values)

    def alias(self, name: str, annotation: object):
        return self.root.alias(name, annotation)

    def array_schema(self, name: str, item_type: object):
        return self.root.array_schema(name, item_type)

    def project_schema(self, name: str, source, *steps: ProjectionStep):
        return self.root.project_schema(name, source, *steps)

    def failure(self, name: str, code: str, *, schema=None, message: str | None = None):
        return self.root.failure(name, code, schema=schema, message=message)

    def event(self, name: str, declaration: EventDeclaration | None = None):
        return self.root.event(name, declaration)

    def policy(self, name: str, declaration: PolicyDeclaration | None = None):
        return self.root.policy(name, declaration)

    def operation(self, name: str, declaration: OperationDeclaration | None = None):
        return self.root.operation(name, declaration)

    def storage(self, name: str, declaration: StorageDeclaration):
        return self.root.storage(name, declaration)

    def source(self, name: str, declaration: ValueSourceDeclaration):
        return self.root.source(name, declaration)

    def view(self, name: str, declaration: ViewDeclaration | None = None):
        return self.root.view(name, declaration)

    def workflow(self, name: str, declaration: WorkflowDeclaration):
        return self.root.workflow(name, declaration)

    def presentation(self, name: str, declaration: PresentationDeclaration):
        return self.root.presentation(name, declaration)

    def compile(self) -> AuthoringResult:
        return compile_author(self)


__all__ = ["Author"]
