---
title: Codepotg.yaml configuration
description: Configure defaults, tasks, inputs, outputs, templates, cleanup, commands, environment, and frontend selection.
product: codepotg
package: codepotg
order: 4
---

# `Codepotg.yaml` configuration

CodepotG discovers one of these files in the current working directory:

```text
Codepotg.yaml
Codepotg.yml
```

If both exist, the command fails and asks for one explicit config. An explicit path can be passed with `--config`.

## Root shape

```yaml
allow: true

defaults:
  language: typescript
  output: ./generated

tasks:
  sdk:
    input: ./openapi.json
    output: ./generated/sdk
```

## `allow`

`allow` must be exactly `true` before generation can mutate the project or run commands.

```yaml
allow: true
```

Missing, false, or non-boolean values do not grant permission.

## `defaults`

`defaults` is an optional object merged into every task before task-specific values are validated.

```yaml
defaults:
  language: typescript
  templateDir: ./templates/typescript
  env:
    GENERATED_BY: codepotg
```

Task fields override defaults at the top level. Nested objects are not deep-merged unless their owning field explicitly implements that behavior.

## `tasks`

`tasks` must be a non-empty mapping. The mapping key is the task name.

```yaml
tasks:
  api-sdk:
    description: Generate the TypeScript API client
    input: ./contracts/openapi.json
    language: typescript
    templateDir: ./templates/typescript
    output: ./src/generated/api
    frontend: admin
    clean:
      - ./src/generated/api
    env:
      API_PACKAGE: '@acme/api'
```

### Required task fields

| Field | Type | Meaning |
|---|---|---|
| `input` | path string | OpenAPI JSON or YAML source |
| `language` | string | Bundled or registered language adapter |
| `output` | path string | Task output root |

Relative paths resolve from the configuration directory.

### Optional task fields

| Field | Type | Meaning |
|---|---|---|
| `templateDir` | path string | Project-owned template pack |
| `templates` | path string | Compatibility alias for `templateDir` |
| `clean` | path list | Paths eligible for explicit refresh cleanup |
| `before` | command list | Commands before rendering/writes |
| `after` | command list | Commands after successful generation |
| `env` | string map | Environment values for task and commands |
| `description` | string | Human-readable task purpose |
| `frontend` | string | Selected authored frontend, or `*` where supported |

## Commands

A command can be a string:

```yaml
before:
  - pnpm lint:generated
```

or an object:

```yaml
after:
  - name: Format generated files
    run: pnpm prettier --write src/generated
    cwd: .
    optional: false
    env:
      NODE_ENV: development
```

Command fields:

| Field | Meaning |
|---|---|
| `name` | Optional display name |
| `run` | Required shell command |
| `cwd` | Optional working directory relative to config |
| `optional` | Continue when this command fails |
| `env` | Command-specific environment values |

Review commands as executable project code. Dry runs and `--skip-before`/`--skip-after` prevent their execution.

## Frontend selection

```yaml
frontend: admin
```

The name must refer to explicitly authored frontend metadata in the normalized contract.

```yaml
frontend: '*'
```

Use `*` only when the task intentionally exposes all authored frontends.

## Multiple tasks

```yaml
tasks:
  backend:
    input: ./openapi.json
    language: typescript
    templateDir: ./templates/backend
    output: ./apps/api/src/generated

  customer-web:
    input: ./openapi.json
    language: next
    templateDir: ./templates/customer
    output: ./apps/web/src/generated
    frontend: customer

  mobile:
    input: ./openapi.json
    language: dart
    output: ./apps/mobile/lib/generated
```

Run one task by name or all tasks in file order.

## Legacy filename rejection

`CodepotFile.yml` and `CodepotFile.yaml` are reserved for the TypeScript runtime. CodepotG reports a clear configuration error rather than guessing which engine should run the file.