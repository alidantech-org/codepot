# Normalized `x-codegen` Metadata

CodepotG treats known `x-codegen` information as language-neutral generation facts. Template authors receive named structures rather than raw extension dictionaries.

The normalized root includes:

```text
resources
base_entities
entities
access_policies
frontends
```

Operations can add:

```text
operation identity and role
parameter target
UI behavior
access use
cache behavior
runtime transport and hooks
data sources
tags
structured information notes
```

Schemas can add:

```text
kind
resource
role
projection
shared
query behavior
```

Unknown extension keys remain available under `extensions` and the original extension object remains under `raw`.

## Resources

Resource definitions normalize:

```text
id
name
path
route
tags
ui
access_policies
hooks
operations
schemas
entities
info
extensions
raw
```

Path-level resource references are resolved to the root definition. The original reference remains available.

Resource defaults can contribute to operation effective values, but authored operation values remain distinguishable from inherited values.

## Operation identity

Operation metadata normalizes:

```text
name
role
tags
```

Supported role views include list, detail, create, update, delete, action, query, mutation, and unknown. Roles can be authored or inferred. The origin is retained.

## Parameter target

An operation can identify a combined parameter schema:

```text
operation.parameters.target
operation.query_schema
operation.params_schema
```

The target retains its original ref and resolved schema. Individual OpenAPI parameters remain available independently.

## UI metadata

Resources and operations expose:

```text
enabled
infer
inferred
role
effective_enabled
inference_source
inference_reason
```

The effective value is computed before templates render. Templates do not merge resource and operation settings.

## Access policies

Policy definitions and policy uses are separate.

Definitions:

```text
api.access_policies
resource.access_policies
```

Policy facts:

```text
id
name
owner
context
roles
permissions
tags
public
authenticated
info
extensions
raw
```

Operation use:

```text
operation.access.ref
operation.access.policy
operation.access.is_resolved
```

Global and resource-scoped policies use the same normalized structure.

## Cache behavior

Cache metadata is represented by a read policy and an invalidation policy.

```text
operation.cache.enabled
operation.cache.read
operation.cache.invalidate
```

Read policy:

```text
enabled
ttl_seconds
stale_seconds
scope
key_fields
tags
```

Invalidation policy:

```text
operation_names
operations
resource_names
resources
tags
all
```

Authored operation names are preserved. Resolved operation objects are added after all operations are registered. Unknown targets remain visible and produce diagnostics.

## Runtime transport

Runtime transport requirements expose:

```text
operation.runtime.transport.inbound.ip
operation.runtime.transport.inbound.user_agent
operation.runtime.transport.inbound.headers
operation.runtime.transport.inbound.cookies
operation.runtime.transport.outbound.cookies
operation.runtime.transport.outbound.headers
```

Transport metadata describes facts required by generated handlers or clients. It does not execute runtime behavior inside CodepotG.

## Runtime hooks

Resource hook definitions and operation hook uses are normalized separately.

Lifecycle views:

```text
operation.runtime.hooks.before_handler
operation.runtime.hooks.after_success
operation.runtime.hooks.after_error
```

Each use exposes:

```text
ref
hook
phase
order
is_resolved
```

Hook order is deterministic. Templates do not resolve hook references or reorder lifecycle phases.

## Data sources

Named operation sources normalize response-list information:

```text
id
name
response_field
item
key_field
label_field
value_field
description
extensions
raw
```

Collections expose:

```text
operation.sources.all
operation.sources.by_name
operation.primary_source
```

The item schema uses the common schema-use shape and is resolved before rendering.

## Query capabilities

Entity and schema fields can expose:

```text
exact
one_of
sortable
selectable
date
range
search.prefix
search.contains
search.fuzzy
operators
```

CodepotG preserves authored capabilities and derives a normalized operator list. Templates can use either the source capability or the operator view.

## Base entities

Base entities use the same normalized entity contract as concrete entities. They add:

```text
abstract
kind
visibility
declared_fields
extends
```

Concrete entity inheritance is resolved before rendering. Each entity exposes declared, inherited, and effective field views.

## Entity definitions

Entity metadata normalizes:

```text
resource
schema
store
visibility
extends
fields
backend_fields
relations
constraints
info
extensions
raw
```

### Field behavior

Entity fields can expose:

```text
role
generated
unique
indexed
readonly
editable
managed
immutable
selectable
query
constraints
backend_only
```

Effective defaults and explicit authored flags remain distinguishable.

### Backend fields

Backend-only fields remain separate from public fields. Templates can choose:

```text
entity.backend_fields
entity.storage_fields
entity.public_fields
entity.fields
```

A frontend pack does not receive backend-only fields through the public view accidentally.

### Relations

Relations normalize:

```text
cardinality
target
local_fields
foreign_fields
on_delete
on_update
nullable
owning
inverse
is_to_one
is_to_many
```

Single-field authored relations are represented as one-item field collections so composite relations can be supported without changing the public structure.

### Constraints and rules

Storage constraints expose:

```text
kind
fields
unique
rule
```

Rules use a recursive expression structure:

```text
op
field
value
args
condition
then
otherwise
op_raw
raw_arguments
```

Known rule operations receive convenience flags. Unknown operations are preserved and reported rather than dropped.

## Entity visibility

Visibility is explicit and can include backend, storage, API, frontend, or project-defined extensions. Derived views include:

```text
is_abstract
is_persistent
is_backend_visible
is_storage_visible
```

## Schema metadata

Known schema extension facts expose:

```text
kind
resource
role
shared
projection
```

Projection information can expose:

```text
source
include
exclude
rename
partial
```

Schema role helpers include request, response, query, params, body, model, DTO, enum, primitive, and unknown.

## Frontends

Frontends normalize:

```text
name
title
route_prefix
folders
components
screens
operations
schemas
info
extensions
raw
```

Components normalize props, schema uses, operation uses, tags, and notes. Screens normalize routes, full routes, params, query schemas, component placement, operation uses, tags, and notes.

CodepotG exposes explicitly authored frontends only. It does not invent screens or components.

## Structured information notes

Information categories normalize to:

```text
explain
access
implement
validation
security
observability
ux
performance
testing
other
```

Unknown categories remain ordered under `other` with their original name and entries.

## Normalization rule

```text
known extension fact      -> named normalized property
reference                 -> original ref plus resolved target
missing optional section  -> safe empty structure
unknown x-codegen key     -> extensions
complete original object  -> raw
malformed value           -> raw plus diagnostic
```

No known metadata should require direct dictionary traversal in ordinary templates.
