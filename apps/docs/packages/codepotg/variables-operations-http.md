---
title: Operation and HTTP variables
description: Complete reference for operations, parameters, request bodies, responses, media types, sources, cache, and query targets.
product: codepotg
package: codepotg
order: 12
---

# Operation and HTTP variables

## Operation collections

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

## Operation values

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

Derived values:

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

Use `role` and derived classification instead of inferring behavior only from HTTP method or operation name.

## Parameters

Each parameter exposes:

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

`location` distinguishes path, query, header, and cookie values. Effective path parameters include both path-level and operation-level declarations while preserving their source location.

## Request bodies

```text
request_body.ref
request_body.required
request_body.description
request_body.content_types
request_body.media_types
request_body.schema_refs
request_body.docs
request_body.lang
request_body.emit
request_body.extensions
request_body.raw
```

## Responses

Each response exposes:

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

`primary_response` is the normalized preferred success response. Templates that emit complete clients should still inspect all relevant responses.

## Media types

```text
content_type
schema
example
examples
encoding
extensions
raw
```

Use media-type-specific schemas when one operation returns different representations.

## Security

Operation security preserves explicit overrides and inherited API-level requirements. Empty operation security can intentionally mean public access.

## Sources

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

Sources help templates generate selectors, relation inputs, or data-loading helpers without hardcoding response inspection.

## Cache

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

Resolved operation and resource targets are available after the registry is complete.

## Query targets

Operations can expose normalized query, params, body, and response schemas through:

```text
query_schema
params_schema
body_schema
response_schema
parameters.target
target
```

## Example service template

```jinja
export async function {{ operation.name.camel }}(
  input: {{ operation.body_schema.name.pascal if operation.body_schema else "void" }}
): Promise<{{ operation.response_schema.name.pascal }}> {
  return client.request({
    method: "{{ operation.method }}",
    path: "{{ operation.path }}",
    body: input,
  });
}
```

Real packs should use language and import helpers rather than assuming TypeScript names directly.