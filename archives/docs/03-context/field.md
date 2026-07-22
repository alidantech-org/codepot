---
title: Field Context
description: Working with field-level data in templates
---

# Field Context

Field context provides data about individual entity fields.

## Field Structure

```codepurify
{| field.names.* |} // Name transformations {| field.flags.* |} // Boolean flags
{| field.typescript.* |} // TypeScript type info
```

## Names

```codepurify
{| field.names.original |} // "firstName" {| field.names.casing.camel |} //
"firstName" {| field.names.casing.pascal |} // "FirstName" {|
field.names.casing.snake |} // "first_name" {| field.names.casing.kebab |} //
"first-name"
```

## Flags

Common boolean flags:

```codepurify
{| field.flags.is_string |} // true for string fields {| field.flags.is_number
|} // true for numeric fields {| field.flags.is_boolean |} // true for boolean
fields {| field.flags.is_date |} // true for date fields {|
field.flags.is_nullable |} // true for optional fields {|
field.flags.is_required |} // true for required fields {| field.flags.is_primary
|} // true for primary keys {| field.flags.is_unique |} // true for unique
fields
```

## TypeScript Types

```codepurify
{| field.typescript.type |} // "string | null" {| field.typescript.base_type |}
// "string"
```

## Field Loop Example

```codepurify
{|#each entity.fields.arrays.all.items as field|} {|#if field.flags.is_primary|}
@PrimaryGeneratedColumn() {|field.names.casing.camel|}: number; {|else if
field.flags.is_string|} {|#if field.flags.is_nullable|} @IsOptional() {|/if|}
@IsString() {|field.names.casing.camel|}: {|#if field.flags.is_nullable|}string
| null{|else|}string{|/if|}; {|else if field.flags.is_number|} @IsNumber()
{|field.names.casing.camel|}: number; {|/if|} {|/each|}
```

## Conditional Usage with Flags

```codepurify
{|#if field.flags.is_string|} // String field logic @IsString() {|/if|} {|#if
field.flags.is_nullable|} @IsOptional() // Make type nullable
{|field.names.casing.camel|}: string | null; {|else|}
{|field.names.casing.camel|}: string; {|/if|} {|#if field.flags.is_unique|}
@IsUnique() {|/if|}
```

Field context enables precise, conditional generation based on field characteristics.
