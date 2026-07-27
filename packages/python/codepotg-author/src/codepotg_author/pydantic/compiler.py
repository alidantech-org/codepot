from __future__ import annotations

from enum import Enum
from types import NoneType, UnionType
from typing import Any, Union, get_args, get_origin, get_type_hints

from pydantic import BaseModel

from codepotg_author.refs import GroupRef, SchemaRef
from codepotg_author.schemas import (
    FieldDeclaration,
    FieldOptions,
    SchemaDeclaration,
    SchemaDeclarationKind,
)


class PydanticCompiler:
    def __init__(self, author: Any, *, group: GroupRef | None = None) -> None:
        self._author = author
        self._group = group
        self._compiled: dict[type[object], SchemaRef[object]] = {}
        self._enum_refs: dict[type[Enum], SchemaRef[object]] = {}

    def compile(self, model: type[object], *, name: str | None = None) -> SchemaRef[object]:
        if not isinstance(model, type) or not issubclass(model, BaseModel):
            raise TypeError("pydantic_model requires a Pydantic v2 BaseModel subclass")
        existing = self._compiled.get(model)
        if existing is not None:
            return existing
        schema_name = name or model.__name__
        ref = self._author.schema(schema_name, {}, group=self._group)
        self._compiled[model] = ref
        hints = get_type_hints(model, include_extras=True)
        fields: list[FieldDeclaration] = []
        for field_name, model_field in model.model_fields.items():
            annotation = hints.get(field_name, model_field.annotation)
            normalized = self._normalize_annotation(annotation)
            options = self._field_options(model_field, annotation)
            if isinstance(normalized, SchemaRef):
                fields.append(FieldDeclaration(field_name, schema_ref=normalized, options=options))
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
            existing = self._enum_refs.get(annotation)
            if existing is not None:
                return existing
            ref = self._author.enum_schema(annotation.__name__, annotation, group=self._group)
            self._enum_refs[annotation] = ref
            return ref
        origin = get_origin(annotation)
        args = get_args(annotation)
        if origin in {list, set, frozenset} and args:
            return origin[self._normalize_annotation(args[0])]
        if origin is dict and len(args) == 2:
            return dict[
                self._normalize_annotation(args[0]),
                self._normalize_annotation(args[1]),
            ]
        if origin is tuple and args:
            normalized = tuple(self._normalize_annotation(item) for item in args)
            return tuple[normalized]
        if origin in {UnionType, Union} and args:
            return annotation
        return annotation

    @staticmethod
    def _field_options(model_field: Any, annotation: object) -> FieldOptions:
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
