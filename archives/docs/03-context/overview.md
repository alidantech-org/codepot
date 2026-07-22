---
title: Context Overview
description: Understanding Codepurify's structured context system
---

# Context Overview

Context is the structured data that templates consume during code generation.

## What is Context?

Context provides deterministic, type-safe data to templates through a hierarchical object structure.

## Root Objects

- **entity** - Current entity being processed (names, fields, relations)
- **field** - Field data when inside field loops
- **relation** - Relation data when inside relation loops
- **global** - System-wide data and configuration

## Deterministic Structure

Context is predictable and unambiguous:

```codepurify
{| entity.names.casing.pascal |} // Always available {| field.flags.is_string |}
// Available in field loops {| relation.kind |} // Available in relation loops
```

No runtime ambiguity - context paths are validated before generation.

## Simplified Context Tree

```json
{
  "entity": {
    "names": {
      "original": "user",
      "casing": { "camel": "user", "pascal": "User" }
    },
    "fields": {
      "arrays": {
        "all": {
          "items": [
            {
              "names": { "camel": "email" },
              "flags": { "is_string": true }
            }
          ]
        }
      }
    },
    "relations": {
      "arrays": {
        "all": {
          "items": [
            {
              "names": { "pascal": "Profile" },
              "kind": "one-to-one"
            }
          ]
        }
      }
    }
  },
  "global": {
    "templates": { "current": { "name": "user-dto" } }
  }
}
```

## How Templates Consume Context

Templates access context through dot notation:

```codepurify
export class {| entity.names.casing.pascal |}DTO { {|#each
entity.fields.arrays.all.items as field|} {|field.names.casing.camel|}: {|#if
field.flags.is_string}string{|/if|}; {|/each|} }
```

Context drives every aspect of generation - names, types, conditions, and structure.
