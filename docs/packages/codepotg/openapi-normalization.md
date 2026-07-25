---
title: OpenAPI normalization and preservation
description: Understand how CodepotG preserves OpenAPI 3.0/3.1, JSON Schema, refs, extensions, raw values, and diagnostics without silent loss.
product: codepotg
package: codepotg
order: 15
---

# OpenAPI normalization and preservation

CodepotG provides a normalized contract while preserving original OpenAPI information.

Every major object follows three layers:

```text
normalized named fields
extensions
raw
```

## Preservation rules

| Source information | Destination |
|---|---|
| Known OpenAPI field | Named normalized property |
| Known JSON Schema keyword | Named schema or constraint property |
| Known `x-codegen` field | Named Codepot property |
| Unknown `x-*` field | `extensions` |
| Unknown ordinary field | `raw` plus diagnostic |
| Original `$ref` | Preserved ref value |
| Resolved `$ref` | Resolved target |
| Explicit `null` | Presence-aware value |
| Missing value | Explicit unset state |
| Malformed value | Raw value plus diagnostic |

## Root raw document

```text
api.raw
```

Use `api.raw` only as a forward-compatibility escape hatch. Prefer normalized values whenever CodepotG understands the field.

## Object raw values

Normalized objects also expose local raw source:

```text
resource.raw
schema.raw
field.raw
operation.raw
parameter.raw
request_body.raw
response.raw
media_type.raw
entity.raw
relation.raw
constraint.raw
access_policy.raw
frontend.raw
screen.raw
component.raw
```

## Extensions

Unknown extension keys remain available under `extensions` with original names. Known `x-codegen` metadata is normalized first.

## References

Reference normalization preserves:

```text
ref
kind
name
owner
is_resolved
target
```

Circular references remain references rather than recursively expanding the graph.

## Presence-aware values

Values such as defaults, consts, examples, nullable settings, UI settings, cache settings, security overrides, and entity behavior can be absent or explicitly null.

Presence-aware values expose:

```text
value
is_set
origin
```

## OpenAPI root

The normalized root preserves:

```text
openapi
json_schema_dialect
info
servers
paths
webhooks
components
security
tags
external_docs
extensions
raw
```

## Components

All reusable component registries remain addressable:

```text
schemas
responses
parameters
examples
request_bodies
headers
security_schemes
links
callbacks
path_items
```

## JSON Schema

CodepotG preserves known identity, annotation, validation, array, object, composition, condition, and reference keywords from OpenAPI 3.0 and 3.1.

Important groups include:

```text
$schema, $id, $anchor, $dynamicAnchor
 type, const, enum, format
 numeric and string constraints
 items, prefixItems, contains
 properties, additionalProperties, patternProperties
 allOf, anyOf, oneOf, not, if, then, else
 $ref, $dynamicRef, circular refs
```

## Version compatibility

OpenAPI 3.0 and 3.1 represent nullability, exclusive bounds, schema dialects, and JSON Schema support differently. CodepotG records:

```text
source OpenAPI version
source representation
normalized effective meaning
```

Templates should render normalized meaning unless the target specifically needs source-version behavior.

## Diagnostics

```text
api.diagnostics.unresolved
api.diagnostics.raw_only
api.diagnostics.unsupported
api.diagnostics.malformed
api.diagnostics.loss
```

A value can be unsupported and still preserved. Silent loss is the unacceptable condition.

The intended invariant is:

```text
api.diagnostics.loss.count == 0
```

## Template guidance

Use values in this order:

1. normalized property;
2. normalized derived view;
3. extension;
4. local raw object;
5. root raw document.

Document any template dependency on raw-only values so it can migrate when a normalized field becomes available.