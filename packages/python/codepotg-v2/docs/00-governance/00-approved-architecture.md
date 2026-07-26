# Approved CodepotG v2 architecture

This document is the highest-priority design contract for the clean rewrite under `packages/python/codepotg-v2`.

An implementation that conflicts with this document is incorrect even when it resembles the existing generator.

## Clean-room boundary

- The existing `packages/python/codepotg` package remains the complete implementation for old behavior.
- CodepotG v2 does not import old implementation modules.
- CodepotG v2 does not implement compatibility decoders for old `tasks` configuration or `paths.yaml`.
- Existing packs may be studied for real requirements, but are re-authored into the v2 contracts.

## Two authored YAML files

1. `codepotg.yaml` contains project-owned configuration.
2. `CodepotgPack.yaml` contains pack-owned configuration.

No registry alias file or extra user-edited pack configuration is required.

## Project ownership

`codepotg.yaml` owns:

- project identity;
- named semantic inputs;
- executable names or paths;
- command policy and project before/after commands;
- ordered pack instances;
- each pack instance's direct source, input, output root, options, bindings, and project-owned overrides.

A pack instance declares its source directly:

```yaml
source:
  local: ./packs/typescript-sdk
```

or:

```yaml
source:
  git: https://github.com/alidantech-org/codepotg-packs.git
  ref: typescript-sdk/v2.4.1
  path: packs/typescript-sdk
```

`source` locates the pack. `input` names the semantic project source consumed by the pack.

## Pack ownership

`CodepotgPack.yaml` owns only information that cannot be inferred safely from the pack filesystem:

- pack identity, compatibility, description, options, and public bindings;
- include/exclude rules;
- registered emission selections;
- pack-relative emission paths;
- fixed data selectors;
- explicit generated import dependencies;
- exported emission groups and declared symbols;
- executable defaults and exact before/after command arguments.

The manifest does not register every template or static file.

## Filesystem-driven templates

The default content root is `templates/`.

- Literal template paths are rendered at the same relative output path.
- The recognized template-engine suffix is removed.
- Literal static and binary files are copied unchanged.
- `_partials/` is available to templates and is not emitted.
- A pack-root `.gitignore` and manifest `include`/`exclude` rules control discovery.
- A literal `.gitignore` control file is not emitted. A pack that generates one authors `.gitignore.jinja`.

Only folders whose whole segment is `{selectionKey}` require a manifest entry.

## Selection folders and output roots

A registered selection has the compact form:

```yaml
selections:
  repositories:
    paths: [src, repositories]
    select: entities.each
```

The physical source path:

```text
templates/{repositories}/(entity.name.kebab.s).repository.ts.jinja
```

may emit, relative to the configured pack-instance output root:

```text
src/repositories/order.repository.ts
```

The final project path is:

```text
<pack instance output>/src/repositories/order.repository.ts
```

`{root}` is a built-in selection folder that contributes no path segments and emits at the pack-instance output root.

## Fixed selectors

CodepotG exposes a documented fixed selector registry rather than arbitrary `from`/`as` declarations.

Examples:

```text
resources.each
resources.all
entities.each
entities.all
schemas.models.each
schemas.dtos.each
schemas.enums.each
operations.each
resource.entities.each
resource.operations.each
```

`.each` repeats the selection and exposes the known singular context. `.all` emits once with the collection. An optional alias may be supplied inline, for example `entities.each(repositoryEntity)`.

## Path expressions

Path and filename values use one expression syntax:

```text
(entity.name.kebab.s)
(resource.name.path.o)
(option.clientName)
```

Double parentheses escape literal parentheses:

```text
((admin)) -> (admin)
```

Square brackets remain literal, allowing Next.js routes such as `[id]`, `[...slug]`, and `[[...slug]]` without escaping.

Semantic records do not expose invented `fileName`, `filePath`, or `directory` properties.

## Names and inflection

Named semantic items expose deterministic case projections:

```text
raw, clean, snake, kebab, camel, pascal,
screaming, constant, dot, path, lower, upper
```

Each projection exposes:

```text
o/original, s/singular, p/plural, number
```

Naming and inflection are behavior-versioned and participate in lock/cache identity.

## Imports, exports, and symbols

Cross-selection imports are mandatory and explicit:

```yaml
imports:
  entities: entities
  types: typesIndex
```

The mapping is `localName: selectionKey`. Only declared providers may satisfy generated dependencies. The resolver chooses the least required symbols, respects selection scope/cardinality, rejects conflicts, and asks the language adapter to produce target-language imports.

Barrels are normal templates registered through an emission selection:

```yaml
repositoriesIndex:
  paths: [src, repositories]
  exports: [repositories]
```

`exports` is an ordered list of selection keys. Barrels may export ordinary selections or other barrels. The template receives emitted paths and declared symbols and controls wildcard versus explicit exports and their textual order.

Generated symbols are declared explicitly; CodepotG does not parse rendered source to guess them.

## Commands and executables

Commands contain exact opaque arguments authored by the project or pack:

```yaml
commands:
  after:
    install:
      executable: packageManager
      arguments: [add, typeorm@^0.3.0]
```

CodepotG does not transform dependency maps into package-manager arguments and does not understand npm, pnpm, Dart, Flutter, or other install syntax in core.

A pack may provide executable defaults. The project may provide or replace executable names/paths. Host security policy remains authoritative, and downloaded pack commands require approval by default.

## Git sources and locking

There is no separate `registries` plus `use` indirection. Every pack instance carries one direct source:

- `source.local` for a local directory;
- `source.git` plus required `ref` and optional repository-relative `path` for Git-hosted packs.

Branches and tags resolve to immutable commits in `codepotg.lock.yaml`. The lock records the requested source, resolved commit, pack identity/version, subdirectory, content digest, plugin/behavior versions, and no credentials.

## Adapter boundary

- Source adapters normalize semantic inputs into neutral IR.
- Core owns selector resolution, filesystem discovery, path expressions, dependency graphs, planning, safety, and locking.
- Language adapters implement target imports/exports, module paths, types, literals, comments, and filename validation.
- Template-engine adapters render already planned contexts and do not choose destinations.
- Pack providers resolve local and generic Git sources using controlled snapshots.

## Planning and safety

Before rendering, CodepotG validates configuration, pack identity, selectors, destinations, imports, exports, symbols, commands, approvals, collisions, and lock drift. Invalid plans never call renderers or writers.

## Agent rule

Every agent must read this document, the relevant detailed design, the matching task ledger, and `tasks/PARALLEL_WORK.md` before implementation. Design changes require explicit approval and matching documentation/task updates before code is written.
