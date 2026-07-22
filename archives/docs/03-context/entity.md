---
title: Entity Context
description: Working with entity-level data in templates
---

# Entity Context

Entity context contains all data about the current entity being processed.

## Entity Structure

```codepurify
{| entity.names.* |} // Name transformations {| entity.fields.* |} // Field data
and arrays {| entity.relations.* |} // Relation data and arrays
```

## Names

```codepurify
{| entity.names.original |} // "userProfile" {| entity.names.casing.camel |} //
"userProfile" {| entity.names.casing.pascal |} // "UserProfile" {|
entity.names.casing.snake |} // "user_profile" {| entity.names.casing.kebab |}
// "user-profile" {| entity.names.singular.casing.pascal |} // "User" {|
entity.names.plural.casing.pascal |} // "Users"
```

## Fields

```codepurify
{| entity.fields.arrays.all.items |} // All fields {|
entity.fields.arrays.by_kind.string.items |} // String fields only {|
entity.fields.counts.all |} // Total field count {|
entity.fields.counts.required |} // Required field count
```

## Relations

```codepurify
{| entity.relations.arrays.all.items |} // All relations {|
entity.relations.arrays.one_to_many.items |} // One-to-many relations {|
entity.relations.arrays.many_to_one.items |} // Many-to-one relations
```

## Example Template

```codepurify
export class {| entity.names.casing.pascal |}Entity { {|#each
entity.fields.arrays.all.items as field|} {|#if field.flags.is_required|}
@IsNotEmpty() {|/if|} {|field.names.casing.camel|}: {|#if
field.flags.is_string}string{|/if|}; {|/each|} {|#each
entity.relations.arrays.one_to_many.items as relation|} {|relation.property|}:
{|relation.names.casing.pascal|}[]; {|/each|} }
```

## How Entity Drives Generation

Entity context determines:

- Class names (`entity.names.casing.pascal`)
- Property types (`field.flags.is_string`)
- Relation mappings (`relation.property`)
- Validation rules (`field.flags.is_required`)

Every generated file starts from the entity context.
