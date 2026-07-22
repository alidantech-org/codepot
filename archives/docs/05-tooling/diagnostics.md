---
title: Diagnostics
description: Real-time error detection and validation
---

# Diagnostics

The extension provides real-time error detection for Codepurify template syntax and context paths.

## Error Types

### Invalid Context Paths

❌ Invalid:

```txt
{| entity.names.casings.camel |}
```

✅ Valid:

```txt
{| entity.names.casing.camel |}
```

### Unknown Variables

❌ Invalid:

```txt
{| entity.unknown_property |}
```

✅ Valid:

```txt
{| entity.names.original |}
```

### Syntax Errors

❌ Invalid:

```txt
{|#if condition|}
content
{|#if|}
```

✅ Valid:

```txt
{|#if condition|}
content
{|/if|}
```

## Error Display

Errors appear as:

- **Red underline** — syntax errors
- **Yellow underline** — warnings
- **Hover tooltip** — error description

## Real-Time Validation

Errors are detected as you type:

```txt
{| entity. |}
{| entity.names. |}
{| entity.names.casings.camel |}
```

The first two examples are incomplete but not necessarily invalid while typing. The final example is invalid because `casings` is not a valid property.

## Common Validation Rules

### Casing Properties

Use `casing`, not `casings` or `case`.

```txt
{| entity.names.casing.camel |}
```

Invalid examples:

```txt
{| entity.names.casings.camel |}
{| entity.names.case.camel |}
```

### Array Access

Use the normalized array structure.

```txt
{| entity.fields.arrays.all.items |}
```

Invalid example:

```txt
{| entity.fields.items |}
```

### Control Flow Tags

Control flow blocks must have matching opening and closing tags.

```txt
{|#if condition|}
content
{|/if|}
```

Invalid example:

```txt
{|#if condition|}
content
{|#if|}
```

## Error Messages

Hover over diagnostics to see detailed messages, such as:

- `"casings" is not a valid property of "entity.names"`
- `Missing closing tag for "if"`
- `Unknown variable "unknown_property"`

## Performance

Validation runs in the background without affecting typing performance. Large files are processed incrementally.
