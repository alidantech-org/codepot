---
title: Autocomplete
description: Intelligent autocomplete for template variables and keywords
---

# Autocomplete

The extension provides intelligent autocomplete inside template expressions.

## Variable Suggestions

Type `entity.` to see available properties:

```codepurify
{| entity. |} // ↓ Shows: // - names // - fields // - relations
```

Continue typing for nested suggestions:

```codepurify
{| entity.names. |} // ↓ Shows: // - original // - casing // - singular // -
plural
```

## Keyword Suggestions

Control flow keywords appear automatically:

```codepurify
{|# |} // ↓ Shows: // - if // - each // - raw
```

## Field Loop Autocomplete

Inside field loops, get field-specific suggestions:

```codepurify
{|#each entity.fields.arrays.all.items as field|} {| field. |} // ↓ Shows: // -
names // - flags // - typescript {|/each|}
```

## Snippets

Common patterns expand with snippets:

### DTO Class

Type `dto` + Tab:

```codepurify
export class {| entity.names.casing.pascal |}DTO { {|#each
entity.fields.arrays.all.items as field|} {|field.names.casing.camel|}: {|#if
field.flags.is_string}string{|/if|}; {|/each|} }
```

### Validation Decorator

Type `val` + Tab:

```codepurify
{|#if field.flags.is_string|} @IsString() {|/if|} {|field.names.casing.camel|}:
string;
```

## Context-Aware Suggestions

Autocomplete adapts to current context:

- **Entity level** - `entity.*` properties
- **Field level** - `field.*` properties
- **Relation level** - `relation.*` properties
- **Global level** - `global.*` properties

## Limitations

- Autocomplete requires valid context files
- Complex nested paths may not show all options
- Custom context variables need manual typing
