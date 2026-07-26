# `codepotg.yaml` project specification

## Purpose

`codepotg.yaml` is the only user-authored project configuration file required by CodepotG v2. It registers semantic sources, project toolchains, security policy, global lifecycle commands, and configured pack instances.

It does not describe internal templates and does not select one global language.

## Canonical shape

```yaml
apiVersion: codepotg.dev/v2
kind: Project

metadata:
  name: defytickets-organiser
  description: Generated clients and application integrations.

allow: true

sources:
  backendApi:
    adapter: openapi
    path: ../backend/sdk/openapi/openapi.v1.yaml
    options: {}

variables:
  productName: DefyTickets

toolchains:
  node:
    version: ">=20"
    packageManager: pnpm
  dart:
    sdk: ">=3.5.0 <4.0.0"

security:
  commands:
    project: allow
    packs: requireApproval
  dependencyLifecycleScripts: requireApproval

commands:
  before:
    - id: generate-openapi-spec
      name: Generate OpenAPI specification
      cwd: ../backend
      executable: pnpm
      arguments: [exec, codepot-openapi, generate]
  after:
    - id: validate-complete-project
      executable: pnpm
      arguments: [typecheck]
      optional: true

packs:
  server:
    use:
      path: ../backend/sdk/next
    source: backendApi
    enabled: true
    profile: modular
    output:
      root: ./_
    clean:
      - gen
    options:
      generateExamples: false
    bindings:
      common:
        from:
          barrel: "@modules/common"
        symbols:
          baseRepository: BaseRepository
          logger: AppLogger
    overrides:
      languages:
        typescript:
          imports:
            aliases:
              "@": ./src
    commands:
      before: []
      after:
        - id: lint-generated
          action: node.eslint.fix
          paths: ["{output.root}/gen/**/*.{ts,tsx}"]
          optional: true
```

## Root fields

### `apiVersion`

Required. Selects the typed project schema. Initial value:

```text
codepotg.dev/v2
```

### `kind`

Required and exactly `Project`.

### `metadata`

Required identity object:

- `name`: stable project name;
- `description`: optional human description;
- namespaced metadata extensions may be added only through registered extension schemas.

### `allow`

Required explicit generation permission. Generation does not write files when `allow` is false. Validation, configuration, and plan inspection remain available.

### `sources`

Named semantic inputs. Each source specifies:

- source adapter ID;
- local path, in-memory identity, or adapter-supported locator;
- adapter-owned typed options;
- optional declared digest or freshness policy.

Packs reference a source by name. Several packs may use the same normalized source without reparsing it.

### `variables`

Project-owned values intentionally exposed to pack options or declared binding inputs. Variables are typed at the consuming contract. They are not an unrestricted template-global dictionary.

### `toolchains`

Project environment selections such as:

- Node version and package manager;
- Dart SDK;
- Python interpreter/package tool;
- Java JDK/build tool;
- formatter or linter choices where standardized.

Packs declare compatible capabilities. The project selects the actual tool when needed.

### `security`

Project-requested policy. Host policy remains authoritative and may tighten every field.

### `commands`

Project-global commands:

- `before` runs once before configured packs;
- `after` runs once after all selected packs complete and commit according to phase rules.

These are project-owned, not pack-owned.

### `packs`

Ordered mapping of project pack instances. The key is a project-local instance ID, so the same pack can be configured multiple times.

## Pack instance fields

### `use`

Required pack locator. Supported planned forms:

```yaml
use:
  path: ./packs/server
```

```yaml
use:
  github: alidantech-org/codepotg-nestjs-pack
  ref: v2.1.0
  path: packs/server
```

```yaml
use:
  git:
    url: git@github.com:alidantech-org/private-packs.git
    ref: main
    path: packs/server
```

The resolved immutable commit and digest belong in `codepotg.lock`.

### `source`

Name of a project source consumed by the pack. A pack that creates only static scaffolding may omit it when its contract allows no semantic source.

### `enabled`

Optional boolean, default true.

### `profile`

Optional pack-defined profile such as `modular`, `monolithic`, or `minimal`. A profile selects declared file descriptors or defaults; it does not select a language.

### `output`

Pack-instance output configuration:

- `root` required unless the pack owns the project root by contract;
- optional mount or package path;
- instance-specific lifecycle restrictions.

All pack output paths resolve beneath the effective root unless explicitly allowed by host policy.

### `clean`

Project-approved relative clean scopes for this pack. Pack declarations may suggest managed roots, but the project and host control destructive cleanup.

### `options`

Values for the pack's public typed option schema. Unknown options are errors.

### `bindings`

Project values satisfying the pack's public binding catalog. Supported shapes are determined by binding kind and language adapter contracts.

Example module import:

```yaml
bindings:
  baseRepository:
    symbol: BaseRepository
    from:
      module: "@modules/common/base"
```

Example real project path, allowing relative-path calculation:

```yaml
bindings:
  baseRepository:
    symbol: BaseRepository
    from:
      projectPath: src/modules/common/base-repository.ts
```

Example default barrel for several binding IDs:

```yaml
bindings:
  common:
    from:
      barrel: "@modules/common"
    symbols:
      baseRepository: BaseRepository
      logger: AppLogger
```

### `overrides`

Typed project overrides allowed by adapter and pack policy. Common scopes:

- `languages` for project-wide target-syntax conventions used by this pack instance;
- `templateEngines` for safe engine options allowed by the engine and pack;
- `templates` for explicitly exposed template-level options, output destinations, or local rules.

Overrides are typed patches, not recursively merged YAML.

### `commands`

Project-owned commands associated with this pack instance. They run around only this configured instance and use project-command trust policy.

## Execution order

The default lifecycle is:

1. project global `before` commands;
2. pack instance project-owned `before` commands;
3. pack-owned approved setup/before actions;
4. pack planning and generation;
5. pack-owned approved after actions;
6. pack instance project-owned `after` commands;
7. next pack;
8. project global `after` commands.

Exact transaction phase placement must be declared by each action. Commands that mutate generated staging content run before commit. Commands intended to validate committed project state run after commit and cannot be described as part of an atomic file transaction.

## Configure command ownership

`codepotg configure` reads pack manifests, detects project toolchains and candidate bindings, asks typed setup questions, and writes answers directly under the matching `packs.<instance>` entry in `codepotg.yaml`.

It does not create another editable pack configuration file.

## Validation

Validation must report:

- unknown project and pack fields;
- missing sources;
- duplicate or invalid instance IDs;
- unresolved pack locators;
- invalid options or bindings;
- incompatible toolchain constraints;
- forbidden overrides;
- unsafe output or clean paths;
- command capability and approval requirements;
- lock drift.

## Non-goals

`codepotg.yaml` does not contain:

- project-level `language`;
- internal template file lists;
- pack-internal selections;
- old `tasks` entries;
- a `templateDir` field;
- arbitrary raw YAML passed directly to templates.
