# Lossless OpenAPI Preservation

CodepotG will expose a complete normalized contract while preserving the original OpenAPI document without silent data loss.

The public model uses three layers on every major object:

```text
normalized fields
extensions
raw
```

## Preservation rules

| Source information | Public destination |
| --- | --- |
| Known OpenAPI field | Named normalized property |
| Known JSON Schema keyword | Named schema or constraint property |
| Known `x-codegen` field | Named Codepot property |
| Unknown `x-*` field | `extensions` |
| Unknown non-extension field | `raw` plus diagnostic |
| Original `$ref` | Preserved reference value |
| Resolved `$ref` | Resolved target |
| Explicit `null` | Presence-aware value |
| Missing value | Explicit unset state |
| Malformed value | Preserved raw value plus diagnostic |

## Canonical raw document

The complete source document remains available through:

```text
api.raw
```

The raw root is an escape hatch for forward compatibility. Template packs should prefer normalized properties whenever CodepotG understands the information.

## Object-level raw data

Major objects also preserve their source object:

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

Object-level raw data makes forward-compatible custom packs possible without requiring a search through the root document.

## Extensions

Unknown extension values are separated from ordinary raw data:

```text
api.extensions
resource.extensions
schema.extensions
operation.extensions
entity.extensions
frontend.extensions
```

Known Codepot extension values are normalized first. Unknown or project-specific `x-*` keys remain available by original key.

## Reference preservation

Reference normalization never replaces the original reference.

```text
ref
kind
name
owner
is_resolved
target
```

This applies to schemas, parameters, request bodies, responses, headers, examples, links, security schemes, resources, operations, access policies, hooks, entities, frontends, and project-specific extension references.

Resolution is completed after the relevant registry is available. Circular references remain valid and are represented without recursively expanding the target.

## Presence-aware values

A source value can be absent or explicitly set to `null`. These cases are not equivalent.

Presence-aware values expose:

```text
value
is_set
origin
```

They are used for:

```text
default
const
example
nullable settings
security overrides
UI settings
cache settings
entity field behavior
```

## OpenAPI document information

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

Standard values receive named properties. Unsupported future fields remain in raw form and produce informational diagnostics rather than being removed.

## Components

All reusable component registries remain available:

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

Normalized domain collections may provide easier views, but the complete component inventory remains addressable.

## Paths and operations

Path-level information preserves:

```text
summary
description
servers
parameters
resource metadata
extensions
raw
```

Operation information preserves:

```text
tags
summary
description
external_docs
operation_id
parameters
request_body
responses
callbacks
deprecated
security
servers
x-codegen metadata
extensions
raw
```

Path parameters and operation parameters are normalized into declared and effective views without discarding their source location.

## JSON Schema support

The normalized schema contract will preserve validation and composition information needed by complete validators and model generators.

### Core identity and annotation

```text
$schema
$id
$anchor
$dynamicAnchor
title
description
default
examples
readOnly
writeOnly
deprecated
```

### Types and values

```text
type
const
enum
format
nullable normalization
```

### Numeric constraints

```text
minimum
maximum
exclusiveMinimum
exclusiveMaximum
multipleOf
```

### String constraints

```text
minLength
maxLength
pattern
contentEncoding
contentMediaType
contentSchema
```

### Array constraints

```text
items
prefixItems
contains
minContains
maxContains
minItems
maxItems
uniqueItems
unevaluatedItems
```

### Object constraints

```text
properties
required
additionalProperties
patternProperties
propertyNames
minProperties
maxProperties
dependentRequired
dependentSchemas
unevaluatedProperties
```

### Composition and conditions

```text
allOf
anyOf
oneOf
not
if
then
else
```

### Reference and recursion

```text
$ref
$dynamicRef
recursive and circular references
```

Known keywords become normalized typed facts. Keywords not yet normalized remain available in raw form with a diagnostic marked as preserved.

## OpenAPI schema compatibility

OpenAPI 3.0 and 3.1 differ in nullability, exclusive bounds, schema dialect behavior, and supported JSON Schema keywords. CodepotG normalizes both into one stable contract while retaining:

```text
source OpenAPI version
source representation
normalized effective meaning
```

Templates should render normalized meaning and may inspect the source version only when the target output needs version-specific behavior.

## Diagnostics

Normalization diagnostics expose:

```text
path
severity
code
message
preserved
source_kind
```

Classified views include:

```text
api.diagnostics.unresolved
api.diagnostics.raw_only
api.diagnostics.unsupported
api.diagnostics.malformed
api.diagnostics.loss
```

The required completion condition is:

```text
api.diagnostics.loss.count == 0
```

An unsupported value is acceptable only when it is preserved. A silently discarded value is not acceptable.

## Template author guidance

Use this order:

1. normalized property;
2. normalized derived view;
3. extension value;
4. object raw value;
5. root raw document.

Template packs that depend on raw-only values should document the expected extension or OpenAPI version so they can migrate when a normalized property is added.
