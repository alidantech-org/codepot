---
title: Context Reference
description: Complete reference of available context paths
---

# Context Reference

## entity

| Path | Description |
|------|-------------|
| entity.names.original | Original entity name |
| entity.names.casing.camel | camelCase name |
| entity.names.casing.pascal | PascalCase name |
| entity.names.casing.snake | snake_case name |
| entity.names.casing.kebab | kebab-case name |
| entity.names.casing.constant | CONSTANT_CASE name |
| entity.names.casing.title | Title Case name |
| entity.names.singular.casing.camel | Singular camelCase |
| entity.names.singular.casing.pascal | Singular PascalCase |
| entity.names.plural.casing.camel | Plural camelCase |
| entity.names.plural.casing.pascal | Plural PascalCase |
| entity.fields.arrays.all.items | All field items |
| entity.fields.arrays.all.length | Total field count |
| entity.fields.arrays.by_kind.string.items | String field items |
| entity.fields.arrays.by_kind.number.items | Number field items |
| entity.fields.arrays.by_kind.boolean.items | Boolean field items |
| entity.fields.arrays.by_kind.date.items | Date field items |
| entity.fields.arrays.by_query.required.items | Required field items |
| entity.fields.arrays.by_query.optional.items | Optional field items |
| entity.fields.arrays.by_query.unique.items | Unique field items |
| entity.fields.counts.all | Total field count |
| entity.fields.counts.required | Required field count |
| entity.fields.counts.optional | Optional field count |
| entity.relations.arrays.all.items | All relation items |
| entity.relations.arrays.all.length | Total relation count |
| entity.relations.arrays.one_to_one.items | One-to-one relations |
| entity.relations.arrays.one_to_many.items | One-to-many relations |
| entity.relations.arrays.many_to_one.items | Many-to-one relations |
| entity.relations.arrays.many_to_many.items | Many-to-many relations |

## field

| Path | Description |
|------|-------------|
| field.names.original | Original field name |
| field.names.casing.camel | camelCase name |
| field.names.casing.pascal | PascalCase name |
| field.names.casing.snake | snake_case name |
| field.names.casing.kebab | kebab-case name |
| field.names.casing.constant | CONSTANT_CASE name |
| field.names.casing.title | Title Case name |
| field.flags.is_string | Field is string type |
| field.flags.is_number | Field is number type |
| field.flags.is_boolean | Field is boolean type |
| field.flags.is_date | Field is date type |
| field.flags.is_nullable | Field is nullable |
| field.flags.is_required | Field is required |
| field.flags.is_primary | Field is primary key |
| field.flags.is_unique | Field is unique |
| field.flags.is_auto_increment | Field auto-increments |
| field.flags.is_email | Field is email format |
| field.flags.is_url | Field is URL format |
| field.flags.is_uuid | Field is UUID format |
| field.typescript.type | TypeScript type string |
| field.typescript.base_type | Base TypeScript type |
| field.typescript.nullable_type | Nullable TypeScript type |
| field.index | Field index in array |
| field.constraints.min | Minimum value constraint |
| field.constraints.max | Maximum value constraint |
| field.constraints.min_length | Minimum length constraint |
| field.constraints.max_length | Maximum length constraint |

## relation

| Path | Description |
|------|-------------|
| relation.names.original | Original relation name |
| relation.names.casing.camel | camelCase name |
| relation.names.casing.pascal | PascalCase name |
| relation.names.casing.snake | snake_case name |
| relation.names.casing.kebab | kebab-case name |
| relation.names.casing.constant | CONSTANT_CASE name |
| relation.names.casing.title | Title Case name |
| relation.kind | Relation type (one-to-one, etc.) |
| relation.target | Target entity name |
| relation.target_entity | Target entity PascalCase |
| relation.property | Property name on source |
| relation.property.casing.camel | Property camelCase |
| relation.property.casing.pascal | Property PascalCase |
| relation.module.path | Module import path |
| relation.module.name | Module name |
| relation.module.import_name | Module import name |
| relation.index | Relation index in array |

## global

| Path | Description |
|------|-------------|
| global.templates.current.name | Current template name |
| global.templates.current.type | Current template type |
| global.templates.current.output_path | Current template output path |
| global.templates.all.count | Total template count |
| global.templates.all.arrays.items | All template items |
| global.config.project.name | Project name |
| global.config.project.version | Project version |
| global.config.output.directory | Output directory |
| global.config.validation.enabled | Validation enabled flag |
| global.config.debug.enabled | Debug mode flag |
| global.utils.string.to_pascal | String to PascalCase utility |
| global.utils.string.to_camel | String to camelCase utility |
| global.utils.string.to_snake | String to snake_case utility |
| global.utils.path.normalize | Path normalization utility |
| global.utils.path.join | Path joining utility |
