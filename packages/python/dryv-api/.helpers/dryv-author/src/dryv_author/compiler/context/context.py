from __future__ import annotations

from types import NoneType, UnionType
from typing import Any, Union, get_args, get_origin

from dryv.ir import KernelData, Provenance, SemanticId, TypeExpression, TypeKind
from dryv.ir.diagnostics import Diagnostics

from dryv_author.core import AuthorMetadata, AuthorRef, Declaration, DeclarationRegistry, FieldRef, RefKind, SchemaRef, slug
from dryv_author.validation.diagnostics import author_error


class CompilerContext:
    def __init__(self, metadata: AuthorMetadata, registry: DeclarationRegistry) -> None:
        self.metadata = metadata
        self.registry = registry
        self._normalized: dict[str, object] = {}
        self._compiled: dict[str, object] = {}
        self._diagnostics: list[object] = []

    def declarations(self, kind: RefKind) -> tuple[Declaration, ...]:
        return self.registry.by_kind(kind)

    def declaration(self, ref: AuthorRef[object]) -> Declaration:
        return self.registry.require(ref)

    def owned(self, owner_id: str) -> tuple[Declaration, ...]:
        return self.registry.by_owner(owner_id)

    def payload(self, declaration: Declaration, expected: type[Any]) -> Any:
        if not isinstance(declaration.payload, expected):
            raise TypeError(f"{declaration.kind.value} {declaration.id!r} payload must be {expected.__name__}")
        return declaration.payload

    def normalized_payload(self, declaration: Declaration, expected: type[Any]) -> Any:
        value = self._normalized.get(declaration.id, declaration.payload)
        if not isinstance(value, expected):
            raise TypeError(f"normalized payload for {declaration.id!r} must be {expected.__name__}")
        return value

    def set_normalized(self, declaration_id: str, value: object) -> None:
        self._normalized[declaration_id] = value

    def put_compiled(self, declaration: Declaration, value: object) -> None:
        self._compiled[declaration.id] = value

    def compiled_for(self, declarations: tuple[Declaration, ...], kind: RefKind) -> tuple[Any, ...]:
        return tuple(self._compiled[item.id] for item in declarations if item.kind is kind and item.id in self._compiled)

    def semantic_id(self, ref: AuthorRef[object]) -> SemanticId:
        declaration = self.registry.require(ref)
        return SemanticId(declaration.id)

    def field_id(self, ref: FieldRef[object]) -> SemanticId:
        if ref.author_key != self.metadata.key:
            raise ValueError("field reference belongs to another Author")
        schema = self.registry.get(ref.schema_declaration_id)
        if schema is None or schema.kind is not RefKind.SCHEMA:
            raise ValueError(f"field reference has unknown schema {ref.schema_declaration_id!r}")
        from dryv_author.features.schemas import SchemaDeclaration
        source = self.normalized_payload(schema, SchemaDeclaration)
        if ref.field_name not in {item.name for item in source.fields}:
            raise ValueError(f"schema {schema.name!r} has no field {ref.field_name!r}")
        return SemanticId(ref.declaration_id)

    def type_expression(self, annotation: object | None) -> TypeExpression:
        if isinstance(annotation, TypeExpression):
            return annotation
        if isinstance(annotation, SchemaRef):
            return TypeExpression.reference_to(self.semantic_id(annotation))
        if annotation is str:
            return TypeExpression.primitive("string")
        if annotation is int:
            return TypeExpression.primitive("integer")
        if annotation is float:
            return TypeExpression.primitive("number")
        if annotation is bool:
            return TypeExpression.primitive("boolean")
        if annotation is bytes:
            return TypeExpression.primitive("bytes")
        if annotation is object:
            return TypeExpression.primitive("object")
        if annotation is Any:
            return TypeExpression.primitive("unknown")
        if annotation is NoneType:
            return TypeExpression.primitive("null")
        origin = get_origin(annotation)
        args = get_args(annotation)
        if origin in {list, set, frozenset} and args:
            return TypeExpression.array_of(self.type_expression(args[0]))
        if origin is dict and len(args) == 2:
            return TypeExpression.map_of(self.type_expression(args[0]), self.type_expression(args[1]))
        if origin is tuple and args:
            return TypeExpression.tuple_of(*(self.type_expression(item) for item in args if item is not Ellipsis))
        if origin in {UnionType, Union} and args:
            members = tuple(self.type_expression(item) for item in args)
            return members[0] if len(members) == 1 else TypeExpression.union_of(*members)
        if isinstance(annotation, type):
            return TypeExpression.primitive(annotation.__name__.lower())
        if annotation is None:
            return TypeExpression(TypeKind.UNKNOWN)
        raise TypeError(f"unsupported author type annotation: {annotation!r}")

    def kernel_data(self, declaration: Declaration, *, pointer: str | None = None) -> KernelData:
        source = declaration.source or self.metadata.source
        if source is None:
            return KernelData(provenance=Provenance("dryv-author", self.metadata.name, pointer=pointer))
        joined = source.pointer
        if joined and pointer:
            joined = f"{joined}/{pointer}"
        elif pointer:
            joined = pointer
        return KernelData(provenance=Provenance("dryv-author", source.source_id, pointer=joined))

    def error(self, code: str, message: str, declaration: Declaration | None = None) -> None:
        self._diagnostics.append(author_error(code, message, declaration))

    @property
    def diagnostics(self) -> Diagnostics:
        return Diagnostics.from_iterable(self._diagnostics)

    @staticmethod
    def slug(value: str) -> str:
        return slug(value)


__all__ = ["CompilerContext"]
