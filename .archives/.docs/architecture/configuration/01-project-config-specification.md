# `dryv.yaml` project specification

## Purpose

`dryv.yaml` is the project-owned orchestration file. It names semantic contracts, executable names or paths, security policy, project commands, and ordered pack instances.

It does not list pack templates, selection folders, generated symbols, or one global target language.

## Current canonical shape

```yaml
apiVersion: dryv.dev/v1

name: defytickets-generated

sources:
  contract:
    adapter: ir
    file: ./contract.dryv.yaml

executables:
  packageManager: pnpm
  flutter: flutter
  dart: dart

security:
  packCommands: approve

packs:
  backendRepositories:
    source:
      local: ./packs/typeorm-repositories
    input: contract
    output: apps/backend

    options:
      repositoryStyle: class

    bindings:
      baseRepository:
        from: src/database/base.repository.ts
        symbol: BaseRepository

  typescriptSdk:
    source:
      git: https://github.com/alidantech-org/dryv-packs.git
      ref: typescript-sdk/v2.4.1
      path: packs/typescript-sdk
    input: contract
    output: packages/typescript-sdk

  flutterSdk:
    source:
      git: https://github.com/alidantech-org/dryv-pack-flutter-sdk.git
      ref: v1.4.2
    input: contract
    output: apps/mobile

commands:
  after:
    formatWorkspace:
      executable: packageManager
      arguments: [exec, prettier, --write, packages/typescript-sdk]
      optional: true
```

## Root fields

### `apiVersion`

Required schema version. Current value: `dryv.dev/v1`.

### `name`

Required project identity used in diagnostics, plans, reports, and lock metadata.

### `sources`

Named semantic inputs. The built-in `ir` adapter strictly decodes a canonical Dryv contract:

```yaml
sources:
  contract:
    adapter: ir
    file: ./contract.dryv.yaml
```

Several pack instances may consume the same input through `input`.

A planned contract-provider model will also support configured Python callables and host-supplied in-memory contracts without requiring an intermediate file. Until that public configuration is implemented, the built-in canonical IR adapter remains the file-based route.

### `executables`

Project-selected executable names or paths:

```yaml
executables:
  packageManager: pnpm
  flutter: C:/tools/flutter/bin/flutter
```

A declared command may reference one of these keys. Project values replace matching pack defaults. Dryv does not infer command arguments or translate package-manager syntax.

### `security`

Project-requested policy. Host policy remains authoritative. Downloaded pack commands require approval by default.

### `commands`

Project-global commands. `before` runs once before pack generation; `after` runs once after all selected packs.

```yaml
commands:
  after:
    verify:
      executable: packageManager
      arguments: [test]
      optional: true
```

Arguments are opaque strings. Shell parsing is not used unless a separately approved shell mode is introduced.

### `packs`

Ordered mapping of project-local pack instance names. The same pack may be configured more than once.

## Pack instance fields

### `source`

Required direct pack locator. Exactly one form is allowed.

Local pack:

```yaml
source:
  local: ./packs/server-sdk
```

Git pack at repository root:

```yaml
source:
  git: https://github.com/alidantech-org/dryv-pack-flutter-sdk.git
  ref: v1.4.2
```

Git monorepo pack:

```yaml
source:
  git: git@github.com:alidantech-org/private-packs.git
  ref: main
  path: packs/server-sdk
```

Rules:

- `local` is relative to `dryv.yaml`;
- `git` accepts normal HTTPS or SSH Git URLs;
- `ref` is required and may be a branch, tag, or commit;
- `path` is optional and relative to the repository root;
- `local` and `git` may not appear together;
- branches and tags resolve to immutable commits in `dryv.lock.yaml`.

There is no registry alias or `use` indirection.

### `input`

Optional name of a project semantic contract. Static-only packs may omit it.

`input` is distinct from `source`: `source` locates the pack; `input` identifies the semantic data consumed by the pack.

### `output`

Required pack-instance output root relative to the project file:

```yaml
output: packages/typescript-sdk
```

Every pack manifest `paths` array is relative to this output root.

### `options`

Values for the pack's declared public options. Unknown values are errors.

### `bindings`

Project values satisfying public pack bindings. A binding may identify a project module/path and symbol according to installed target adapters.

```yaml
bindings:
  baseRepository:
    from: src/database/base.repository.ts
    symbol: BaseRepository
```

### `executables`

Optional per-instance executable overrides:

```yaml
executables:
  packageManager: ./tools/pnpm
```

Resolution order is instance override, project executable, then pack default.

### `commands`

Optional project-owned commands scoped to this pack instance. They use project trust policy and do not mutate the pack manifest.

## Lifecycle order

1. project `before` commands;
2. pack-instance project `before` commands;
3. approved pack `before` commands;
4. pack planning and generation;
5. approved pack `after` commands;
6. pack-instance project `after` commands;
7. next pack instance;
8. project `after` commands.

The current runtime remains fail-closed until the separate approved command runtime exists.

## Lock ownership

`dryv.lock.yaml` records exact resolved pack snapshots, identities, digests, plugin versions, and behavior versions. Credentials and secrets never enter the lock. Generated output hashes belong to `.dryv/generation-state.json`, not the dependency lock.

See [`../05-distribution/02-git-github-locking-and-trust.md`](../05-distribution/02-git-github-locking-and-trust.md).

## Validation

Validation rejects:

- unknown fields;
- duplicate input or pack names;
- mixed local/Git pack locators;
- missing Git refs;
- unsafe local, repository, subdirectory, or output paths;
- unknown semantic inputs;
- invalid pack options or bindings;
- unknown executable references;
- unapproved commands;
- lock drift.

## Non-goals

`dryv.yaml` does not contain:

- project-level `language`;
- pack-internal template lists;
- arbitrary selector declarations;
- legacy `tasks` entries;
- `templateDir`;
- package-manager dependency conversion logic;
- a separate registry-to-pack mapping.
