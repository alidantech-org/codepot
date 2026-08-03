# Template Variable Reference

This guide defines the target stable variable surface for CodepotG template packs. New variables are added without removing current paths. Compatibility aliases remain available while bundled and project-owned packs migrate.

## Global context

```text
project
api
lang
emit
meta
resources
features
schemas
operations
entities
access
frontends
selected_frontend
selected_frontends
frontend_count
file
```

## `project`

```text
project.name
project.version
project.description
project.lang
project.emit
project.docs
project.meta
```

`project.name` is a full name object. `project.lang` describes the selected target language. `project.emit` describes project-level output behavior. `project.docs` exposes summary, description, examples, and deprecation information.

## `api`

`api` is the canonical normalized language-neutral contract:

```text
api.info
api.servers
api.security
api.security_schemes
api.resources
api.schemas
api.operations
api.entities
api.base_entities
api.access_policies
api.frontends
api.dependencies
api.extensions
api.raw
api.diagnostics
```

### `api.info`

```text
title
openapi_version
api_version
description
terms_of_service
contact
license
external_docs
```

### `api.servers`

Each server exposes:

```text
url
description
variables
extensions
raw
```

### `api.security`

The API-level security requirements are ordered and remain distinct from operation overrides. Each requirement exposes its referenced scheme and scopes.

## `resources`

```text
resources.all
resources.count
resources.by_id
resources.by_name
resources.with_ui
resources.with_hooks
resources.with_entities
resources.with_access
```

Each resource exposes:

```text
id
name
path
path_name
route
tags
ui
access_policies
hooks
operations
schemas
models
dtos
enums
entities
info
docs
lang
emit
extensions
raw
```

`resource.operations` provides classified operation views. `resource.schemas` and `resource.entities` are already linked to the resource.

## `schemas`

```text
schemas.all
schemas.count
schemas.by_id
schemas.by_name
schemas.models
schemas.dtos
schemas.enums
schemas.primitives
schemas.aliases
schemas.unknown
schemas.queries
schemas.params
schemas.bodies
schemas.requests
schemas.responses
schemas.shared
schemas.projected
schemas.composed
schemas.emit_models
schemas.emit_dtos
schemas.emit_enums
```

Each schema exposes:

```text
id
name
ref
kind
resource
role
shared
projection
dependencies
is_alias
alias_of
nullable
type
types
format
constraints
enum_type
enum_values
fields
composition
inherited_refs
has_field_overrides
array
object
query
docs
lang
emit
extensions
raw
```

### Schema constraints

```text
default
const
examples
minimum
maximum
exclusive_minimum
exclusive_maximum
multiple_of
min_length
max_length
pattern
min_items
max_items
unique_items
min_properties
max_properties
read_only
write_only
deprecated
```

`default` and `const` are presence-aware values so an explicit `null` remains different from an absent value.

### Schema composition

```text
kind
branches
refs
inline_branches
is_all_of
is_any_of
is_one_of
is_not
```

Each branch uses the standard schema-use shape and may be a reference or an inline schema.

### Array information

```text
items
prefix_items
contains
min_items
max_items
unique_items
```

### Object information

```text
additional_properties
pattern_properties
property_names
min_properties
max_properties
dependent_required
```

`additional_properties` distinguishes allowed, forbidden, typed, and referenced values.

## `field`

Schema and entity fields expose a consistent core:

```text
id
name
required
nullable
type
schema
constraints
enum_values
description
query
docs
lang
emit
extensions
raw
```

Schema fields additionally expose references, item schemas, and composition information. Entity fields additionally expose persistence and behavior metadata.

## `operations`

```text
operations.all
operations.count
operations.by_id
operations.by_name
operations.queries
operations.mutations
operations.lists
operations.details
operations.creates
operations.updates
operations.deletes
operations.actions
operations.cached
operations.with_sources
operations.with_runtime
operations.with_ui
```

Each operation exposes:

```text
id
name
method
path
role
resource
tags
parameters
request_body
responses
security
access
cache
runtime
sources
ui
info
target
docs
lang
emit
extensions
raw
```

Derived operation properties include:

```text
is_query
is_mutation
has_path_params
has_request_body
path_params
success_responses
error_responses
primary_response
query_schema
params_schema
body_schema
response_schema
primary_source
```

## `parameter`

```text
id
name
location
required
ref
description
deprecated
allow_empty_value
allow_reserved
style
explode
example
examples
schema
docs
lang
emit
extensions
raw
```

## `request_body`

```text
ref
required
description
content_types
media_types
schema_refs
docs
lang
emit
extensions
raw
```

## `response`

```text
status_code
ref
description
content_types
media_types
schema_refs
headers
links
is_success
is_error
docs
lang
emit
extensions
raw
```

## Media types

Each request or response media type exposes:

```text
content_type
schema
example
examples
encoding
extensions
raw
```

## `entities`

```text
entities.all
entities.count
entities.by_id
entities.by_name
entities.abstract
entities.persistent
entities.with_relations
entities.with_constraints
entities.with_backend_fields
entities.queryable
```

Each entity exposes:

```text
id
name
kind
abstract
resource
schema
store
visibility
extends
declared_fields
inherited_fields
fields
backend_fields
storage_fields
public_fields
editable_fields
readonly_fields
queryable_fields
relations
constraints
info
docs
emit
extensions
raw
```

### Entity fields

```text
id
name
schema
type
required
nullable
role
generated
unique
indexed
immutable
readonly
editable
managed
selectable
backend_only
query
constraints
info
declared_on
inherited
explicit
extensions
raw
```

`explicit` records whether behavior flags were authored or supplied by normalization defaults.

### Entity relations

```text
id
name
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
extensions
raw
```

### Entity constraints

```text
id
name
kind
fields
unique
rule
extensions
raw
```

Rule expressions expose their operation, field, value, arguments, condition, result branches, original operation name, and preserved raw arguments.

## `access`

```text
access.all
access.count
access.by_id
access.by_name
access.global
access.resource_scoped
```

Each access policy exposes:

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

An operation access use exposes:

```text
ref
policy
is_resolved
```

## Cache variables

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

Resolved operation and resource targets are provided after the full operation registry exists.

## Runtime variables

```text
operation.runtime.transport
operation.runtime.hooks
```

Transport:

```text
inbound.ip
inbound.user_agent
inbound.headers
inbound.cookies
outbound.cookies
outbound.headers
```

Hooks:

```text
before_handler
after_success
after_error
```

Each hook use exposes its original ref, resolved hook, lifecycle phase, and stable order.

## Source variables

```text
operation.sources.all
operation.sources.count
operation.sources.by_name
operation.primary_source
```

Each source exposes:

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

## Query variables

```text
field.query.enabled
field.query.exact
field.query.one_of
field.query.sortable
field.query.selectable
field.query.date
field.query.range
field.query.search
field.query.operators
```

Search capabilities:

```text
enabled
prefix
contains
fuzzy
```

Operations can also expose a normalized query target through `operation.query_schema` and `operation.parameters.target`.

## UI variables

Resources and operations use the same UI options:

```text
enabled
infer
inferred
role
effective_enabled
inference_source
inference_reason
```

Effective values include inherited resource behavior, while authored and inferred values remain distinguishable.

## Information notes

Any resource, schema, operation, entity, frontend, component, screen, hook, or policy can expose:

```text
info.explain
info.access
info.implement
info.validation
info.security
info.observability
info.ux
info.performance
info.testing
info.other
```

Unknown note categories remain ordered under `other`.

## Frontends

```text
frontends.all
frontends.count
frontends.by_id
frontends.by_name
```

Each frontend exposes:

```text
id
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

Each component exposes:

```text
name
title
description
props
schemas
operations
tags
info
extensions
raw
```

Each screen exposes:

```text
name
title
description
route
full_route
params
query
components
operations
tags
info
extensions
raw
```

Operation uses retain alias, operation id, resolved operation, method, path, purpose, and source metadata.

## `lang`

```text
lang.name
lang.framework
lang.package
lang.features
lang.meta
```

Language adapters can add stable helper groups for type rendering, literals, validation, imports, identifiers, files, comments, documentation, framework integration, and package integration.

## `emit`

```text
emit.output_path
emit.template_root
emit.dry_run
emit.contract_version
emit.current
```

Per-item emission information includes group, item key, ref, resource path, folder path, file name, dependency refs, dependencies, and imports.

## `file`

```text
file.output_path
file.relative_path
file.name
file.stem
file.suffix
file.depth
file.root_prefix
file.group
file.item_key
file.dependencies
file.imports
file.meta
```

## Lossless fields

All normalized major objects expose:

```text
extensions
raw
```

Known values use named properties. Unknown `x-*` values use `extensions`. The original object remains under `raw` as a final compatibility surface. Diagnostics identify unresolved, raw-only, unsupported, or malformed information.
