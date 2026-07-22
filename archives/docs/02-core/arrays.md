---
title: Arrays & Iteration
description: Working with array contexts and iteration
---

# Arrays & Iteration

Arrays provide structured access to collections with consistent metadata.

## Array Structure

All arrays follow this pattern:

```codepurify
{| collection.arrays.name.items |} {| collection.arrays.name.length |}
```

## ArrayItemContext

Each array item includes:

```codepurify
{| item.index |} // Current index {| item.names.* |} // Name transformations {|
item.flags.* |} // Boolean flags
```

## Loop Syntax

### Basic Loop

```codepurify
{|#each entity.fields.arrays.all.items as field|} {|field.index|}:
{|field.names.casing.camel|} {|/each|}
```

### Without Alias

```codepurify
{|#each entity.fields.arrays.all.items|} {|index|}: {|names.casing.camel|}
{|/each|}
```

## Common Arrays

### All Fields

```codepurify
{|#each entity.fields.arrays.all.items as field|} {|field.names.casing.camel|}:
{|#if field.flags.is_string}string{|/if|}; {|/each|}
```

### By Kind

```codepurify
{|#each entity.fields.arrays.by_kind.string.items as field|}
{|field.names.casing.camel|}: string; {|/each|}
```

### By Query

```codepurify
{|#each entity.fields.arrays.by_query.searchable.items as field|}
@Column("{|field.names.casing.snake|}") private {|field.names.casing.camel|}:
string; {|/each|}
```

## Real Template Example

```codepurify
export class {| entity.names.casing.pascal |}DTO { {|#each
entity.fields.arrays.all.items as field|} {|#if field.flags.is_string|} {|#if
field.flags.is_nullable|} @IsOptional() {|/if|} @IsString()
{|field.names.casing.camel|}: {|#if field.flags.is_nullable|}string |
null{|else|}string{|/if|}; {|/if|} {|#if field.flags.is_number|} @IsNumber()
{|field.names.casing.camel|}: number; {|/if|} {|/each|} }
```

## Array Length

```codepurify
{| entity.fields.arrays.all.length |} // Output: 5 {|#if
entity.fields.counts.required > 0|} // Required fields exist {|/if|}
```

## Nested Arrays

```codepurify
{|#each entity.relations.arrays.one_to_many as relation|} {|#each
relation.target.fields.arrays.all.items as field|}
{|relation.names.casing.pascal|}.{|field.names.casing.camel|} {|/each|}
{|/each|}
```
