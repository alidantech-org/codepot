# Bounded Normalized Roots

Selection-graph templates receive bounded public roots rather than the complete compatibility contract.
The full collections required to resolve a `paths.yaml` selection remain internal to the planner.

The stable normalized roots are:

```text
normalized
schema_contract
domains
codegen_contract
entity_contract
frontend_contract
```

These roots are additive. Legacy folder packs may continue using the compatibility template contract while they migrate.

## `normalized`

`normalized` provides the additive source-preserving API view:

```text
normalized.source
normalized.schemas
normalized.operations
normalized.resources
normalized.raw_objects
normalized.diagnostics
normalized.loss_count
normalized.unresolved_count
normalized.raw_only_count
```

Use this root for the current normalized schema, operation, and resource wrappers and for stable source-object lookup.

## `schema_contract`

`schema_contract` provides complete OpenAPI and JSON Schema keyword facts:

```text
schema_contract.all
schema_contract.count
schema_contract.by_id
schema_contract.dialect
schema_contract.diagnostics
schema_contract.unresolved_count
schema_contract.loss_count
```

Each schema exposes:

```text
source
title
summary
description
types
format
nullable
default
const
example
examples
enum
required
numeric constraints
string constraints
content encoding, media type, and schema
items, prefix_items, and contains
array limits and unevaluated_items
properties and pattern_properties
additional_properties
property_names
object limits
dependent_required and dependent_schemas
unevaluated_properties
all_of, any_of, one_of, and not_schema
if_schema, then_schema, and else_schema
defs
discriminator
read_only, write_only, and deprecated
external_docs
schema_id, anchor, dynamic_anchor, dynamic_ref, and dialect
```

Boolean-or-schema boundaries such as `additional_properties`, `unevaluated_items`, and `unevaluated_properties` expose:

```text
kind
value
schema
diagnostics
is_allowed
is_forbidden
is_typed
```

The `kind` value is one of `missing`, `allowed`, `forbidden`, `schema`, or `malformed`.

## `domains`

`domains` provides normalized standard OpenAPI and core domain facts:

```text
servers
security_schemes
root_security
paths
operations
access
base_entities
entities
frontends
all_diagnostics
unresolved_count
```

Use it for effective HTTP parameters, request and response media, security overrides, callbacks, access definitions, and the first typed entity/frontend views.

## `codegen_contract`

`codegen_contract` provides resource and operation `x-codegen` runtime metadata:

```text
codegen_contract.resources
codegen_contract.operations
codegen_contract.hooks
codegen_contract.diagnostics
codegen_contract.unresolved_count
```

Resource metadata includes route, tags, UI settings, access policies, hooks, linked operations, linked schemas, linked entities, notes, and source.

Operation metadata includes:

```text
name_value
role
tags
ui
parameter_target
query_schema
params_schema
body_schema
response_schema
sources
primary_source
cache
access
transport
hooks
notes
source
diagnostics
```

Cache invalidation retains both authored target names and resolved operation/resource references. Missing targets remain visible and contribute diagnostics.

Hook definitions and hook uses are separate. A use exposes the authored ref, resolved definition, phase, order, source, and diagnostics.

## `entity_contract`

`entity_contract` provides persistence-aware entities after inheritance resolution:

```text
entity_contract.base_entities
entity_contract.entities
entity_contract.all
entity_contract.by_id
entity_contract.diagnostics
entity_contract.unresolved_count
entity_contract.cycle_count
```

Each entity exposes:

```text
resource
schema
store
kind
abstract
visibility
extends
declared_fields
inherited_fields
effective_fields
backend_fields
public_fields
storage_fields
editable_fields
readonly_fields
queryable_fields
relations
constraints
notes
source
all_diagnostics
```

Inherited fields preserve deterministic base order. A declared field that replaces an inherited field exposes `overrides` and `override_origin`.

Query capabilities preserve authored operators first, append derived operators, and report unknown operators without dropping them.

Relations support composite `local_fields` and `foreign_fields`, lifecycle actions, nullability, ownership, inverse names, and `is_to_one` / `is_to_many` helpers.

Rule expressions preserve known and unknown operations, nested conditions, result branches, original operation names, and raw arguments.

## `frontend_contract`

`frontend_contract` contains only explicitly authored frontends:

```text
frontend_contract.all
frontend_contract.count
frontend_contract.by_id
frontend_contract.diagnostics
frontend_contract.unresolved_count
```

Each frontend exposes:

```text
title
route_prefix
folders
components
screens
operations
schemas
notes
source
diagnostics
```

Components expose props, additional schema uses, operation/schema uses, tags, notes, folders, and source.

Screens expose route, `full_route`, params, query, body, response, component names, placement metadata, operation/schema uses, tags, notes, folders, and source.

Linked operation and schema collections contain only successfully resolved authored uses. Missing uses remain on the component or screen with their original refs and diagnostics.

## Common value contracts

Presence-aware values expose:

```text
value
is_set
is_null
origin
source_path
```

References expose:

```text
ref
kind
name
owner
state
target
source_path
diagnostics
is_resolved
```

Schema uses expose:

```text
kind
ref
refs
schema
inline
source_path
diagnostics
is_reference
is_inline
is_resolved
```

Source objects expose:

```text
raw
extensions
diagnostics
source_path
loss_count
```

## Selection context

In addition to bounded globals, each emitted file receives:

```text
selection
emission
selected alias
file
output
providers
provider_outputs
source
sources
resolve
```

`source`, `sources`, and `resolve` are lazy JSONL-backed values. They do not load raw records until the template accesses them.

Templates must not rely on complete OpenAPI traversal through graph globals. Request extra source facts through the permitted lazy resolvers or use the normalized roots above.
