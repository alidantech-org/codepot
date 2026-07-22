---
title: Keywords Reference
description: Complete list of supported template keywords
---

# Control Flow Keywords

| Keyword | Syntax | Description       |
| ------- | ------ | ----------------- | --- | -------------------- |
| if      | `{     | #if condition     | }`  | Conditional block    |
| else    | `{     | #else             | }`  | Alternative block    |
| each    | `{     | #each collection  | }`  | Loop over collection |
| raw     | `{     | {raw}             | }`  | Escape delimiters    |
| unless  | `{     | #unless condition | }`  | Negative conditional |
| with    | `{     | #with object      | }`  | Context switch       |

## Operators

| Operator | Syntax | Description                   |
| -------- | ------ | ----------------------------- | --- | -------------- |
| as       | `{     | #each items as item           | }`  | Alias in loops |
| in       | `{     | #each item in items           | }`  | Loop syntax    |
| and      | `{     | #if condition1 and condition2 | }`  | Logical AND    |
| or       | `{     | #if condition1 or condition2  | }`  | Logical OR     |
| not      | `{     | #if not condition             | }`  | Logical NOT    |
| is       | `{     | #if value is 'test'           | }`  | Equality check |

## Syntax Examples

### If/Else

```codepot
{|#if condition|} content {|else|} alternative {|/if|}
```

### Each Loop

```codepot
{|#each collection as item|} {|item.property|} {|/each|}
```

### Raw Block

```codepot
{|{raw}|} {| this is not parsed |} {|{/raw}|}
```

### Unless

```codepot
{|#unless condition|} content when condition is false {|/unless|}
```

### With

```codepot
{|#with object.nested|} {|property|} {|/with|}
```
