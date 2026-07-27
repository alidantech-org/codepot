from __future__ import annotations

from enum import Enum
from types import NoneType, UnionType
from typing import Any, get_args, get_origin, get_type_hints

from pydantic import BaseModel

from codepotg_author.refs import GroupRef, SchemaRef
from codepotg_author.schemas import FieldDeclaration, FieldOptions, SchemaDeclaration, SchemaDeclarationKind


class PydanticCompiler:
    def __init__(self, author: Any, *, group: GroupRef | None = None) -> None:
        self._author = author
        self._group = group
        self._compiled: dict[type[object], SchemaRef[object]] = {}
        self._visiting: set[type[object]] = set()

    def compile(self, model: type[object], *, name: str | None = None) -> SchemaRef[object]:
        if not isinstance(model, type) or not issubclass(model, BaseModel):
            raise TypeError("pydantic_model requires a Pydantic v2 BaseModel subclass")
        existing = self._compiled.get(model)
        if existing is not None:
            return existing
        schema_name = name or model.__name__
        ref = self._author.schema(schema_name, {}, group=self._group)
        self._compiled[model] = ref
        self._visiting.add(model)
        try:
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
        finally:
            self._visiting.discard(model)
        return ref

    def _normalize_annotation(self, annotation: object) -> object:
        origin = get_origin(annotation)
        args = get_args(annotation)
        if isinstance(annotation, type) and issubclass(annotation, BaseModel):
            return self.compile(annotation)
        if isinstance(annotation, type) and issubclass(annotation, Enum):
            return self._author.enum_schema(annotation.__name__, annotation, group=self._group)
        if origin in {list, set, frozenset} and args:
            return list[self._normalize_annotation(args[0])]  # type: ignore[valid-type]
        if origin is dict and len(args) == 2:
            return dict[self._normalize_annotation(args[0]), self._normalize_annotation(args[1])]  # type: ignore[valid-type]
        if origin is tuple and args:
            return tuple[tuple(self._normalize_annotation(item) for item in args)]  # type: ignore[valid-type]
        if origin in {UnionType, None} and args:
            return annotation
        if origin is not None and args:
            rebuilt = tuple(self._normalize_annotation(item) for item in args)
            if origin is UnionType:
                return annotation
            try:
                return origin[rebuilt]
            except TypeError:
                return annotation
        return annotation

    @staticmethod
    def _field_options(model_field: Any, annotation: object) -> FieldOptions:
        metadata = tuple(model_field.metadata)
        values: dict[str, object] = {}
        for item in metadata:
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
        return FieldOptions(
            required=model_field.is_required(),
            nullable=nullable,
            minimum=values.get("minimum"),  # type: ignore[arg-type]
            maximum=values.get("maximum"),  # type: ignore[arg-type]
            min_length=values.get("min_length"),  # type: ignore[arg-type]
            max_length=values.get("max_length"),  # type: ignore[arg-type]
            pattern=values.get("pattern"),  # type: ignore[arg-type]
            description=model_field.description,
        )
