---
title: Writing Templates
description: How to create codepot templates from scratch
---

# Writing Templates

Create templates that generate structured code from context data.

## File Structure

Templates live in your project's `templates/` folder:

```
templates/
├── user.dto.codepot
├── user.entity.codepot
└── user.service.codepot
```

## Basic Template

Create `templates/user.dto.codepot`:

```codepot
export class {| entity.names.casing.pascal |}DTO { {|#each
entity.fields.arrays.all.items as field|} {|#if field.flags.is_string|}
@IsString() {|field.names.casing.camel|}: string; {|/if|} {|#if
field.flags.is_number|} @IsNumber() {|field.names.casing.camel|}: number;
{|/if|} {|/each|} }
```

## Variable Usage

Access context data using dot notation:

```codepot
{| entity.names.casing.pascal |} // Class name {| field.names.casing.camel |} //
Property name {| field.flags.is_required |} // Boolean condition
```

## Loops

Iterate over collections:

```codepot
{|#each entity.fields.arrays.all.items as field|} private
{|field.names.casing.camel|}: {|#if field.flags.is_string}string{|/if|};
{|/each|}
```

## Conditions

Add conditional logic:

```codepot
{|#if field.flags.is_nullable|} {|field.names.casing.camel|}: string | null;
{|else|} {|field.names.casing.camel|}: string; {|/if|}
```

## Complete Example

Template: `templates/user.entity.codepot`

```codepot
import { Entity, PrimaryGeneratedColumn, Column } from 'typeorm'; @Entity('{|
entity.names.casing.kebab |}') export class {| entity.names.casing.pascal |} {
{|#each entity.fields.arrays.all.items as field|} {|#if field.flags.is_primary|}
@PrimaryGeneratedColumn() {|field.names.casing.camel|}: number; {|else|}
@Column() {|field.names.casing.camel|}: {|#if
field.flags.is_string}string{|/if|}{|#if field.flags.is_number}number{|/if|};
{|/if|} {|/each|} }
```

## Template to Output Mapping

Template + Context → Generated File

- `user.dto.codepot` + `user.json` → `user.dto.ts`
- `user.entity.codepot` + `user.json` → `user.entity.ts`

## Naming Conventions

- Use kebab-case for template files: `user.dto.codepot`
- Use descriptive names: `create-user.dto.codepot`, `update-user.dto.codepot`
- Group related templates: `user/`, `product/`, `order/`
