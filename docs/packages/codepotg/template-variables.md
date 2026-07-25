---
title: Template variable reference
description: Navigate the complete stable CodepotG variable surface by domain.
product: codepotg
package: codepotg
order: 10
---

# Template variable reference

CodepotG exposes normalized, stable template variables grouped by domain. This section splits the complete surface into focused references so template authors do not need one unmanageable page.

## Global values

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

## Reference groups

- [Schemas and fields](/docs/packages/codepotg/variables-schemas-fields)
- [Operations and HTTP values](/docs/packages/codepotg/variables-operations-http)
- [Entities, relations, access, and runtime](/docs/packages/codepotg/variables-entities-access)
- [Frontends, language helpers, and output](/docs/packages/codepotg/variables-frontends-output)

## Root API information

`api.info` exposes:

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

## Servers

Each `api.servers` item exposes:

```text
url
description
variables
extensions
raw
```

## Security

`api.security` preserves ordered API-level requirements. Security schemes remain available through `api.security_schemes`.

Operation security overrides remain distinct from API defaults.

## Resources

Collection views:

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

## Names

Objects with generated identifiers expose a naming object rather than requiring every template to repeat casing logic. Depending on the adapter, common name forms include:

```text
raw
camel
pascal
snake
kebab
plural
singular
path
```

Use the adapter's documented name property or filter. Avoid assuming that a plain `name` string already has target-language casing.

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

## Documentation fields

Major objects expose `docs`, normally including:

```text
summary
description
examples
deprecated
```

## Lossless compatibility

All major normalized objects expose:

```text
extensions
raw
```

Known values use named properties. Unknown `x-*` values use `extensions`. Original source objects remain under `raw`.

## Variable availability

Not every variable exists in every emission. A graph template receives globals, its selection alias, file/emission information, and declared provider outputs. Check for optional values where the OpenAPI source or selected domain does not require them.