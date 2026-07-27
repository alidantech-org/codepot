from __future__ import annotations

from enum import Enum
from types import NoneType, UnionType
from typing import TYPE_CHECKING, Any, Union, cast, get_args, get_origin, get_type_hints

from pydantic import BaseModel
from pydantic.fields import FieldInfo

from codepotg.ir import TypeExpression, TypeKind

from codepotg_author.refs import GroupRef, SchemaRef
from codepotg_author.schemas import (
    FieldDeclaration,
    FieldOptions,
    SchemaDeclaration,
    SchemaDeclarationKind,
)

if TYPE_CHECKING:
    from codepotg_author.author import Author


class PydanticCompiler:
    def __init__(self, author: Author, *, group: GroupRef | None = None) -> None:
        self._author = author
        self._group = group
        self._compiled: dict[type[BaseModel], SchemaRef[object]] = {}
        self._enum_refs: dict[type[Enum], SchemaRef[object]] = {}

    def compile(self, model: type[object], *, name: str | None = None) -> SchemaRef[object]:
        if not issubclass(model, BaseModel):
            raise TypeError("pydantic_model requires a Pydantic v2 BaseModel subclass")
        model_type = cast(type[BaseModel], model)
        existing = self._compiled.get(model_type)
        if existing is not None:
            return existing
        schema_name = name or model_type.__name__
        ref = cast(SchemaRef[object], self._author.schema(schema_name, {}, group=self._group))
        self._compiled[model_type] = ref
        hints = get_type_hints(model_type, include_extras=True)
        fields: list[FieldDeclaration] = []
        for field_name, model_field in model_type.model_fields.items():
            annotation = hints.get(field_name, model_field.annotation)
            normalized = self._normalize_annotation(annotation)
            options = self._field_options(model_field, annotation)
            if isinstance(normalized, SchemaRef):
                fields.append(
                    FieldDeclaration(
                        field_name,
                        schema_ref=cast(SchemaRef[object], normalized),
                        options=options,
                    )
                )
            else:
                fields.append(FieldDeclaration(field_name, annotation=normalized, options=options))
        self._author._replace_payload(
            ref,
            SchemaDeclaration(SchemaDeclarationKind.OBJECT, fields=tuple(fields)),
        )
        return ref

    def _normalize_annotation(self, annotation: object) -> object:
        if isinstance(annotation, type) and issubclass(annotation, BaseModel):
            return self.compile(annotation)
        if isinstance(annotation, type) and issubclass(annotation, Enum):
            enum_type = cast(type[Enum], annotation)
            existing = self._enum_refs.get(enum_type)
            if existing is not None:
                return existing
            ref = cast(
                SchemaRef[object],
                self._author.enum_schema(enum_type.__name__, enum_type, group=self._group),
            )
            self._enum_refs[enum_type] = ref
            return ref
        origin = get_origin(annotation)
        args = get_args(annotation)
        if origin in {list, set, frozenset} and args:
            return TypeExpression.array_of(self._type_expression(args[0]))
        if origin is dict and len(args) == 2:
            return TypeExpression.map_of(
                self._type_expression(args[0]),
                self._type_expression(args[1]),
            )
        if origin is tuple and args:
            members = tuple(
                self._type_expression(item) for item in args if item is not Ellipsis
            )
            return TypeExpression.tuple_of(*members)
        if origin in {UnionType, Union} and args:
            members = tuple(self._type_expression(item) for item in args)
            return members[0] if len(members) == 1 else TypeExpression.union_of(*members)
        return annotation

    def _type_expression(self, annotation: object) -> TypeExpression:
        normalized = self._normalize_annotation(annotation)
        if isinstance(normalized, TypeExpression):
            return normalized
        if isinstance(normalized, SchemaRef):
            return TypeExpression.reference_to(normalized.declaration_id)
        primitives: dict[object, str] = {
            str: "string",
            int: "integer",
            float: "number",
            bool: "boolean",
            bytes: "bytes",
            object: "object",
            Any: "unknown",
            NoneType: "null",
        }
        try:
            primitive = primitives.get(normalized)
        except TypeError:
            primitive = None
        if primitive is not None:
            return TypeExpression.primitive(primitive)
        if isinstance(normalized, type):
            return TypeExpression.primitive(normalized.__name__.lower())
        return TypeExpression(TypeKind.UNKNOWN)

    @staticmethod
    def _field_options(model_field: FieldInfo, annotation: object) -> FieldOptions:
        values: dict[str, object] = {}
        for item in tuple(model_field.metadata):
            for source, target in (
                ("ge", "minimum"),
                ("gt", "minimum"),
                ("le", "maximum"),
                ("lt", "maximum"),
                ("min_length", "min_length"),
                ("max_length", "max_length"),
                ("pattern", "pattern"),
            ):
                value = getattr(item, source, None)
                if value is not None:
                    values[target] = value
        args = get_args(annotation)
        nullable = NoneType in args
        minimum = values.get("minimum")
        maximum = values.get("maximum")
        min_length = values.get("min_length")
        max_length = values.get("max_length")
        pattern = values.get("pattern")
        return FieldOptions(
            required=model_field.is_required(),
            nullable=nullable,
            minimum=minimum if isinstance(minimum, int | float) else None,
            maximum=maximum if isinstance(maximum, int | float) else None,
            min_length=min_length if isinstance(min_length, int) else None,
            max_length=max_length if isinstance(max_length, int) else None,
            pattern=pattern if isinstance(pattern, str) else None,
            description=model_field.description,
        )
