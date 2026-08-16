from dryv.ir import Name, SemanticId, StorageCheck, StorageFieldMapping, StorageIndex, StorageMapping, StorageOnlyField, StorageReferenceMapping, StorageUniqueConstraint

from dryv_author.compiler.context import CompilerContext
from dryv_author.core import Declaration

from .model import StorageDeclaration


def compile_storage(context: CompilerContext, declaration: Declaration) -> StorageMapping:
    source = context.payload(declaration, StorageDeclaration)
    return StorageMapping(id=SemanticId(declaration.id), name=Name(declaration.name), schema=context.semantic_id(source.schema), source=source.source, fields=tuple(StorageFieldMapping(context.field_id(item.field), item.column, item.column_type, item.indexed, item.unique, item.nullable, item.generated, item.computed, item.default) for item in source.fields), primary_key=tuple(context.field_id(item) for item in source.primary_key), indexes=tuple(tuple(context.field_id(field) for field in index) for index in source.indexes), data=context.kernel_data(declaration), storage_fields=tuple(StorageOnlyField(item.name, item.column, item.column_type, item.nullable, item.generated, item.computed, item.default) for item in source.storage_fields), omitted_fields=tuple(context.field_id(item) for item in source.omitted_fields), unique_constraints=tuple(StorageUniqueConstraint(name, columns) for name, columns in source.unique_constraints), storage_indexes=tuple(StorageIndex(name, columns, unique) for name, columns, unique in source.storage_indexes), checks=tuple(StorageCheck(name, expression) for name, expression in source.checks), references=tuple(StorageReferenceMapping(context.field_id(item.field), context.semantic_id(item.target_mapping), context.field_id(item.target_field), item.on_delete) for item in source.references), version_field=context.field_id(source.version_field) if source.version_field else None, serialization=source.serialization)


__all__ = ["compile_storage"]
