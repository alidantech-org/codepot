---
title: Frontend, language, and output variables
description: Complete reference for frontend screens, components, language adapters, emissions, and current file metadata.
product: codepotg
package: codepotg
order: 14
---

# Frontend, language, and output variables

## Frontend collections

```text
frontends.all
frontends.count
frontends.by_id
frontends.by_name
selected_frontend
selected_frontends
frontend_count
```

A task can select one frontend by name or expose all explicitly authored frontends where supported.

## Frontend values

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

## Components

Each frontend component exposes:

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

Operation and schema uses preserve aliases and resolved targets where available.

## Screens

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

Operation uses preserve alias, operation ID, resolved operation, method, path, purpose, and source metadata.

## Selected frontends

- `selected_frontend` is the single explicitly selected frontend when the task chooses one.
- `selected_frontends` is the ordered selected collection.
- `frontend_count` reports its size.

Templates should not infer an unselected frontend from naming conventions.

## `lang`

```text
lang.name
lang.framework
lang.package
lang.features
lang.meta
```

Language adapters can add stable helper groups for:

- type rendering;
- literals;
- validation;
- imports;
- identifiers;
- files;
- comments;
- documentation;
- framework integration;
- package integration.

The exact helper fields depend on the selected adapter. Use the adapter contract rather than calling internal Python utilities from templates.

## `emit`

```text
emit.output_path
emit.template_root
emit.dry_run
emit.contract_version
emit.current
```

Current emission information can include:

```text
group
item_key
ref
resource_path
folder_path
file_name
dependency_refs
dependencies
imports
```

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

`file.output_path` is the planned target. It does not grant unrestricted filesystem access.

## Project metadata

```text
project.name
project.version
project.description
project.lang
project.emit
project.docs
project.meta
```

Use project values for package headers, generated comments, namespaces, and root-level configuration.

## Features

`features` exposes normalized capability flags assembled from source, language, pack, and selected frontend information. Check a feature flag rather than assuming every source includes entities, hooks, or frontend definitions.

## Example screen template

```jinja
export default function {{ screen.name.pascal }}Page() {
  return (
    <main>
      <h1>{{ screen.title }}</h1>
    </main>
  );
}
```

Real templates should consume resolved operations, schemas, parameters, and component providers.

## Guidance

- Keep frontend selection explicit in the task.
- Use `full_route` when the route prefix has already been resolved.
- Generate operation clients from resolved uses, not duplicate IDs.
- Use planned imports and dependencies.
- Keep output paths in `paths.yaml` and file contents in Jinja.
- Treat language helpers as the target-specific boundary.