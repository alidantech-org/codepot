from __future__ import annotations

from dryv.ir import FieldConstraints, Name, Schema, SchemaField, SchemaKind, SemanticId

from dryv_author.compiler.context import CompilerContext
from dryv_author.core import Declaration

from .model import FieldDeclaration, SchemaDeclaration


def compile_schema(context: CompilerContext, declaration: Declaration) -> Schema:
    source = context.normalized_payload(declaration, SchemaDeclaration)
    return Schema(id=SemanticId(declaration.id), name=Name(declaration.name), kind=SchemaKind(source.kind.value), fields=tuple(_compile_field(context, declaration, item) for item in source.fields), enum_values=source.enum_values, item_type=None if source.item_type is None else context.type_expression(source.item_type), alias_of=None if source.alias_of is None else context.type_expression(source.alias_of), literal=source.literal, data=context.kernel_data(declaration), extends=context.semantic_id(source.extends) if source.extends is not None else None)


def _compile_field(context: CompilerContext, schema: Declaration, field: FieldDeclaration) -> SchemaField:
    annotation = field.annotation
    property_id = None
    options = field.options
    capabilities = field.capabilities
    if field.property is not None:
        prop = context.declaration(field.property)
        from dryv_author.features.properties import PropertyDeclaration
        source = context.payload(prop, PropertyDeclaration)
        annotation = source.annotation
        property_id = SemanticId(prop.id)
        if field.options == type(field.options)():
            options = source.options
        if field.capabilities == type(field.capabilities)():
            capabilities = source.capabilities
    elif field.schema is not None:
        context.declaration(field.schema)
        annotation = field.schema
    return SchemaField(id=SemanticId(f"{schema.id}/field/{context.slug(field.name)}"), name=Name(field.name), type=context.type_expression(annotation), required=options.required, nullable=options.nullable, readonly=options.readonly, constraints=FieldConstraints(minimum=options.minimum, maximum=options.maximum, min_length=options.min_length, max_length=options.max_length, pattern=options.pattern, format=options.format), data=context.kernel_data(schema, pointer=f"field:{field.name}"), capabilities=capabilities, property=property_id)


__all__ = ["compile_schema"]
