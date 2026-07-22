---
title: Syntax
description: Codepurify template syntax reference
---

# Codepurify Template Syntax

Codepurify uses `{| ... |}` tags to generate deterministic code from structured data.

## Delimiters

All syntax is defined inside:

```codepurify
{| ... |}
```

These delimiters define expressions, blocks, and comments.

## Expressions

Expressions output values directly into the generated code.

```codepurify
{|entity.name.pascal|}
```

**Rules:**

- Inline only (no automatic spacing or newlines)
- Must resolve to a value at runtime
- No side effects

## Comments

Comments are ignored and not included in output.

### Regular comment

```codepurify
{|# comment #|}
```

### Documentation comment

```codepurify
{|* documentation *|}
```

## Blocks

Blocks control rendering behavior. Each block has an opening and closing tag.

```codepurify
{|if condition|}
...
{|/if|}
```

## `if`

Renders content when a condition is true.

```codepurify
{|if condition|}
...
{|/if|}
```

Supports an optional `else` branch.

**Rules:**

- Must close with `{|/if|}`
- May contain one `{|else|}`

## `unless`

Renders content when a condition is false.

```codepurify
{|unless condition|}
...
{|/unless|}
```

Equivalent to a negated `if`.

**Rules:**

- Must close with `{|/unless|}`
- May contain one `{|else|}`

## `else`

Defines a fallback branch.

```codepurify
{|else|}
```

**Rules:**

- Only valid inside `if` or `unless`
- Cannot exist alone
- Only one allowed per block
- Does not have a closing tag

## `loop`

Repeats content for each item in a collection.

```codepurify
{|loop item in collection|}
...
{|/loop|}
```

**Rules:**

- Must close with `{|/loop|}`
- No automatic separators or formatting
- Output is a direct concatenation of each iteration

## `with`

Changes the current context inside a block.

```codepurify
{|with value|}
...
{|/with|}
```

**Rules:**

- Must close with `{|/with|}`
- Only affects name resolution
- Does not modify data

## `ignore`

Disables all template processing inside the block.

```codepurify
{|ignore|}
...
{|/ignore|}
```

**Rules:**

- Must close with `{|/ignore|}`
- Everything inside is treated as plain text
- No expressions or blocks are evaluated

## Formatting

Codepurify does not apply formatting automatically.

Templates control:

- newlines
- spacing
- indentation

**Principle:**

> Output formatting is explicit and defined by the template.

## Syntax Summary

- `{|value|}` → expression
- `{|# ... #|}` → comment
- `{|* ... *|}` → documentation comment
- `{|if ...|}` / `{|/if|}` → conditional
- `{|unless ...|}` / `{|/unless|}` → inverse conditional
- `{|else|}` → branch
- `{|loop ...|}` / `{|/loop|}` → iteration
- `{|with ...|}` / `{|/with|}` → context scope
- `{|ignore|}` / `{|/ignore|}` → literal block

## Design Principles

Codepurify syntax is intentionally minimal:

- deterministic
- explicit
- easy to validate
- independent of target language formatting

Templates define structure. Formatting remains under user control or external tooling.
