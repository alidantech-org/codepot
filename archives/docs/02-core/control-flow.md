---
title: Control Flow
description: Conditional logic and iteration in templates
---

# Control Flow

Codepurify provides standard control flow structures for dynamic templates.

## If/Else

### Basic If

```codepurify
{|#if entity.fields.flags.has_string|} import { IsString } from
"class-validator"; {|/if|}
```

### If/Else

```codepurify
{|#if field.flags.is_nullable|} {|field.names.casing.camel|}: string | null;
{|else|} {|field.names.casing.camel|}: string; {|/if|}
```

### If/Else If/Else

```codepurify
{|#if field.flags.is_string|} {|field.names.casing.camel|}: string; {|else if
field.flags.is_number|} {|field.names.casing.camel|}: number; {|else|}
{|field.names.casing.camel|}: unknown; {|/if|}
```

## Each Loop

### Simple Loop

```codepurify
{|#each entity.fields.arrays.all.items as field|} {|field.names.casing.camel|}:
{|#if field.flags.is_string}string{|/if|}; {|/each|}
```

### With Index

```codepurify
{|#each entity.fields.arrays.all.items as field|} // Field {|field.index|}
private {|field.names.casing.camel|}: string; {|/each|}
```

### Nested Loops

```codepurify
{|#each entity.relations.arrays.one_to_many as relation|} {|#each
relation.target.fields.arrays.all.items as targetField|}
{|relation.names.casing.pascal|}.{|targetField.names.casing.camel|} {|/each|}
{|/each|}
```

## Raw Blocks

Escape template delimiters when needed:

```codepurify
{|{raw}|} This {| looks like a template |} but isn't {|{/raw}|}
```

## Real DTO Example

```codepurify
export class {| entity.names.casing.pascal |}DTO { {|#each
entity.fields.arrays.all.items as field|} {|#if field.flags.is_string|} {|#if
field.flags.is_nullable|} @IsOptional() {|/if|} @IsString()
{|field.names.casing.camel|}: {|#if field.flags.is_nullable|}string |
null{|else|}string{|/if|}; {|/if|} {|#if field.flags.is_boolean|} @IsBoolean()
{|field.names.casing.camel|}: boolean; {|/if|} {|#if field.flags.is_date|}
@IsDate() {|field.names.casing.camel|}: Date; {|/if|} {|/each|} }
```

## Nested Conditions

```codepurify
{|#each entity.fields.arrays.all.items as field|} {|#if field.flags.is_string|}
{|#if field.flags.is_nullable|} @IsOptional() {|/if|} @IsString()
{|field.names.casing.camel|}: {|#if field.flags.is_nullable|}string |
null{|else|}string{|/if|}; {|/if|} {|/each|}
```

## Loop with Condition

```codepurify
{|#each entity.fields.arrays.all.items as field|} {|#if
field.flags.is_required|} {|field.names.casing.camel|}: {|#if
field.flags.is_string}string{|/if|}; {|/if|} {|/each|}
```
