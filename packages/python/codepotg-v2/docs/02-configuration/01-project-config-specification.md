# `codepotg.yaml` project specification

## Purpose

`codepotg.yaml` is the project-owned configuration file. It names semantic inputs, executable names or paths, command policy, project commands, and ordered pack instances.

It does not list pack templates, selection folders, generated symbols, or one global language.

## Canonical shape

```yaml
apiVersion: codepotg.dev/v2

name: defytickets-generated

sources:
  api:
    adapter: openapi
    file: ./openapi.yaml

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
    input: api
    output: apps/backend

    options:
      repositoryStyle: class

    bindings:
      baseRepository:
        from: src/database/base.repository.ts
        symbol: BaseRepository

  typescriptSdk:
    source:
      git: https://github.com/alidantech-org/codepotg-packs.git
      ref: typescript-sdk/v2.4.1
      path: packs/typescript-sdk
    input: api
    output: packages/typescript-sdk

  flutterSdk:
    source:
      git: https://github.com/alidantech-org/codepotg-pack-flutter-sdk.git
      ref: v1.4.2
    input: api
    output: apps/mobile

commands:
  before:
    refreshOpenApi:
      executable: packageManager
      arguments: [exec, codepot-openapi, generate]
      cwd: ../backend

  after:
    formatWorkspace:
      executable: packageManager
      arguments: [exec, prettier, --write, packages/typescript-sdk]
      optional: true
```

## Root fields

### `apiVersion`

Required schema version. Initial value: `codepotg.dev/v2`.

### `name`

Required project identity used in diagnostics, plans, and lock metadata.

### `sources`

Named semantic inputs. Each entry selects a source adapter and provides its adapter-owned location/options.

```yaml
sources:
  publicApi:
    adapter: openapi
    file: ./specs/public.yaml
```

Several pack instances may consume the same normalized source through `input`.

### `executables`

Project-selected executable names or paths:

```yaml
executables:
  packageManager: pnpm
  flutter: C:/tools/flutter/bin/flutter
```

A pack command may reference one of these keys. Project values replace matching pack defaults.

CodepotG does not infer command arguments from the executable and does not translate package-manager syntax.

### `security`

Project-requested policy. Host policy remains authoritative. Downloaded pack commands require approval by default.

### `commands`

Project-global commands. `before` runs once before pack generation; `after` runs once after all selected packs.

Commands are keyed mappings:

```yaml
commands:
  after:
    verify:
      executable: packageManager
      arguments: [test]
      optional: true
```

Arguments are opaque strings. Shell parsing is not used unless a separately approved shell mode is added later.

### `packs`

Ordered mapping of project-local pack instance names. The same pack may be configured more than once.

## Pack instance fields

### `source`

Required direct pack locator. Exactly one source form is allowed.

Local pack:

```yaml
source:
  local: ./packs/server-sdk
```

Git pack at repository root:

```yaml
source:
  git: https://github.com/alidantech-org/codepotg-pack-flutter-sdk.git
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

- `local` is relative to `codepotg.yaml`;
- `git` accepts normal HTTPS or SSH Git URLs;
- `ref` is required and may be a branch, tag, or commit;
- `path` is optional and relative to the repository root;
- `local` and `git` may not appear together;
- branches and tags are resolved to immutable commits in `codepotg.lock.yaml`.

There is no separate registry alias and no `use` indirection.

### `input`

Optional name of a project semantic source. Static-only packs may omit it.

`input` is intentionally distinct from `source`: `source` locates the pack; `input` locates the semantic data consumed by it.

### `output`

Required pack-instance emission root relative to the project configuration file:

```yaml
output: packages/typescript-sdk
```

Every `paths` array in the pack manifest is relative to this output root.

### `options`

Values for the pack's public options. Unknown values are errors.

### `bindings`

Project values satisfying public pack bindings. A binding may point to a project module/path/barrel and symbol according to the installed language adapter.

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

## Lock ownership

`codepotg.lock.yaml` is generated by CodepotG. It records the exact resolved pack snapshot, identity, digest, and behavior versions. Credentials and secrets never enter the lock.

See [`../05-distribution/02-git-github-locking-and-trust.md`](../05-distribution/02-git-github-locking-and-trust.md).

## Validation

Validation rejects:

- unknown fields;
- duplicate pack instance names;
- mixed local/Git source forms;
- missing Git refs;
- unsafe local, repository, subdirectory, or output paths;
- missing semantic inputs;
- invalid pack options or bindings;
- unknown executable references;
- unapproved commands;
- lock drift.

## Non-goals

`codepotg.yaml` does not contain:

- project-level `language`;
- pack-internal template lists;
- arbitrary selection declarations;
- old `tasks` entries;
- `templateDir`;
- package-manager dependency conversion logic;
- a separate registry-to-pack mapping.
