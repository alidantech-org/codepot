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

```codepurify
{|#if condition|} content {|else|} alternative {|/if|}
```

### Each Loop

```codepurify
{|#each collection as item|} {|item.property|} {|/each|}
```

### Raw Block

```codepurify
{|{raw}|} {| this is not parsed |} {|{/raw}|}
```

### Unless

```codepurify
{|#unless condition|} content when condition is false {|/unless|}
```

### With

```codepurify
{|#with object.nested|} {|property|} {|/with|}
```
