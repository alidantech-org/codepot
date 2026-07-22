---
title: Best Practices
description: Guidelines for writing clean and maintainable templates
---

# Best Practices

## Do

### Use Flags Instead of Raw Conditions

```codepot
{|#if field.flags.is_string|} @IsString() {|/if|}
```

### Use Casing Helpers

```codepot
export class {| entity.names.casing.pascal |} { {|field.names.casing.camel|}:
string; }
```

### Keep Templates Simple

```codepot
{|#each entity.fields.arrays.all.items as field|} {|field.names.casing.camel|}:
{|#if field.flags.is_string}string{|/if|}; {|/each|}
```

### Use Descriptive Aliases

```codepot
{|#each entity.relations.arrays.one_to_many.items as relation|}
{|relation.names.casing.pascal|} {|/each|}
```

## Avoid

### Complex Logic in Templates

❌ Bad:

```codepot
{|#if (field.flags.is_string and field.flags.is_required) or
field.flags.is_primary|}
```

✅ Good:

```codepot
{|#if field.flags.is_required|} @IsNotEmpty() {|/if|}
```

### Deeply Nested Conditions

❌ Bad:

```codepot
{|#if field.flags.is_string|} {|#if field.flags.is_nullable|} {|#if
field.flags.is_unique|} @IsUnique() {|/if|} {|/if|} {|/if|}
```

✅ Good:

```codepot
{|#if field.flags.is_string|} {|#if field.flags.is_nullable|} @IsOptional()
{|/if|} @IsString() {|#if field.flags.is_unique|} @IsUnique() {|/if|} {|/if|}
```

### Hardcoded Strings

❌ Bad:

```codepot
export class User {
```

✅ Good:

```codepot
export class {| entity.names.casing.pascal |} {
```

### Mixed Concerns

❌ Bad:

```codepot
{|#if field.flags.is_string|} import { IsString } from 'class-validator';
{|/each|}
```

✅ Good:

```codepot
import { IsString } from 'class-validator'; {|#each
entity.fields.arrays.all.items as field|} {|#if field.flags.is_string|}
@IsString() {|/if|} {|/each|}
```

## General Guidelines

- Use consistent naming conventions
- Prefer explicit conditions over implicit ones
- Keep templates focused on single responsibility
- Use comments for complex logic
- Test templates with various input contexts
- Maintain consistent indentation and formatting
