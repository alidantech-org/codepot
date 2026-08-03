---
title: Syntax Highlighting
description: Code highlighting for codepot templates
---

# Syntax Highlighting

The extension provides syntax highlighting for codepot template syntax.

## Template Delimiters

`{| ... |}` delimiters are highlighted with distinct colors:

```codepot
export class {| entity.names.casing.pascal |} { {|#each
entity.fields.arrays.all.items as field|} {|field.names.casing.camel|}: string;
{|/each|} }
```

## Highlighted Elements

### Keywords

- `if`, `else`, `each`, `raw` - Control flow keywords
- `true`, `false` - Boolean values

### Variables

- `entity.*` - Entity properties
- `field.*` - Field properties
- `relation.*` - Relation properties
- `global.*` - Global properties

### Comments

```codepot
{|# This is a comment |}
```

## Before/After Example

### Before Extension

```codepot
export class { entity.names.casing.pascal } { {#each
entity.fields.arrays.all.items as field} {field.names.casing.camel}: string;
{/each} }
```

### After Extension

- Delimiters highlighted in blue
- Variables highlighted in orange
- Keywords highlighted in purple
- Comments in gray

## Multi-Language Support

### TypeScript Templates (`.ts.cpt`)

```typescript
// TypeScript syntax preserved
export class {| entity.names.casing.pascal |} {
  {|field.names.casing.camel|}: string;
}
```

### Markdown Templates (`.md.cpt`)

```markdown
# {| entity.names.casing.title |}

{|#each entity.fields.arrays.all.items as field|}

- {|field.names.casing.camel|}
  {|/each|}
```

## Host Language Preservation

The extension maintains host language highlighting while adding template syntax highlighting:

- TypeScript syntax highlighting preserved
- Markdown syntax highlighting preserved
- Template expressions highlighted separately
