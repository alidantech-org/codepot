# `CodepotgPack.yaml` pack specification

## Purpose

`CodepotgPack.yaml` is the complete authored contract for one template pack. It replaces the conceptual role previously held by `paths.yaml`, but v2 does not implement a `paths.yaml` compatibility decoder.

A pack can create a complete runnable project, a standalone package folder, an extension to an existing project, fragments requiring user integration, or any combination of these traits.

## Canonical shape

```yaml
apiVersion: codepotg.dev/v2
kind: TemplatePack

metadata:
  id: alidantech/typeorm-repositories
  version: 1.0.0
  description: Generates TypeORM entities and repositories.

compatibility:
  codepotg: ">=2.0.0 <3.0.0"
  ir: ">=2.0 <3.0"

integration:
  createsProject: false
  ownsFolder: false
  contributesFiles: true
  requiresDependencies: true
  requiresBindings: true
  runnableAlone: false

content:
  root: templates
  ignore:
    - "_authoring/**"
    - "**/*.draft"

writePolicy:
  defaultMode: managed
  managedRoots: [src/generated]
  protectedRoots: []

options:
  repositoryStyle:
    type: enum
    values: [class, functions]
    default: class

languages:
  typescript:
    imports:
      strategy: relative
      omitExtensions: true

  markdown:
    formatting:
      lineWidth: 100

templateEngines:
  jinja:
    undefinedBehavior: error
    whitespace:
      trimBlocks: true
      leftStripBlocks: true

bindings:
  baseRepository:
    kind: import
    target: typescript
    required: true
    title: Base repository
    description: Class extended by generated repositories.
    acceptedSources: [module, projectPath, barrel]
    suggestedSymbol: BaseRepository
    whenMissing: placeholder

selections:
  entities:
    from: entities
    as: entity

filePatterns:
  "{module}/**":
    selection:
      each: modules
      as: module
    output:
      root: src/modules/{module.directory}

files:
  "repositories/repository.ts.jinja":
    role: template
    selection:
      use: entities
    uses:
      bindings: [baseRepository]
    output:
      path: src/repositories/{entity.fileName}.repository.ts

  "index.ts.jinja":
    role: barrel
    selection:
      scope: aggregate
    exports:
      include: [repository]
    output:
      path: src/index.ts

  "_partials/license.txt.jinja":
    role: partial

  ".gitignore":
    role: static

profiles:
  modular:
    enable: [repository, index]

  monolithic:
    enable: [allRepositories]

dependencies:
  node:
    runtime:
      typeorm: "^0.3.0"
    packageManagers:
      supported: [npm, pnpm, yarn]

setup:
  summary: Configure repository dependencies and project bindings.
  documentation: docs/setup.md
  questions:
    - binding: baseRepository
      prompt: Select the base repository export.
  actions:
    before: []
    after:
      - id: ensure-node-dependencies
        action: node.dependencies.ensure
        approval: required
  manualSteps:
    - id: register-repositories
      title: Register generated repositories
      documentation: docs/register-repositories.md

commands:
  after:
    - id: fix-unused-imports
      action: node.eslint.fix
      paths: ["{output.root}/**/*.{ts,tsx}"]
      optional: true

overridePolicy:
  languages:
    typescript:
      imports:
        strategy: allow
        aliases: allow
        omitExtensions: allow
```

## Root fields

### `apiVersion`

Required typed schema version. Initial value `codepotg.dev/v2`.

### `kind`

Required and exactly `TemplatePack`.

### `metadata`

Pack identity and documentation metadata:

- globally meaningful `id`;
- semantic `version`;
- description;
- optional authors, license, repository, homepage, tags, and documentation path.

### `compatibility`

Declared compatibility with core, plugin API, IR, target adapters, and optional ecosystem capabilities. Compatibility is checked before planning.

### `integration`

Composable traits describing how the pack participates in a host project. Traits are descriptive and may be combined; they are not one restrictive enum.

### `content`

Defines pack content roots and ignore behavior.

- `root`: default discovered content directory;
- `ignore`: inline Gitignore-compatible patterns;
- optional `ignoreFile`, usually `.codepotgignore`;
- pack manifest, Git metadata, caches, authoring-only metadata, and task docs are not emitted unless included beneath a content root intentionally.

### `writePolicy`

Pack lifecycle intent:

- default managed, immutable, protected, or unmanaged mode;
- suggested managed roots;
- paths the pack must not overwrite;
- ownership metadata.

The project and host retain authority over destructive clean operations.

### `options`

Public typed pack options. Supported primitive definitions include string, integer, number, boolean, enum, path, list, mapping with typed values, and structured object schemas.

Every option can declare required state, default, validation, description, examples, and setup prompt metadata.

### `languages`

Rules for every target syntax used by the pack. This is a mapping, not a single selected language.

The selected language adapter decodes and validates its own typed rule section. A pack may contain several target languages and data/markup syntaxes.

### `templateEngines`

Engine-specific typed pack rules for engines used by discovered templates. Security-sensitive engine fields remain host-controlled and non-overridable.

### `bindings`

Public binding catalog. The catalog defines meaning, type, documentation, discovery hints, accepted project sources, missing-value behavior, and setup examples.

Individual files list binding IDs under `uses.bindings` so CodepotG can determine exactly which output depends on each project integration.

### `selections`

Named, typed selections over normalized IR or planned artifacts. A selection declares source collection, alias, filtering, ordering, grouping, and supported projection.

Selections are evaluated by the planner, never by arbitrary template code.

### `filePatterns`

Applies defaults to matching discovered files or directories. Folder tokens such as `{module}` can fan out templates and static files over a selection while preserving relative structure.

Pattern precedence is deterministic: broad patterns first, then more specific patterns, then exact `files` configuration.

### `files`

Configuration for discovered pack files. An entry modifies one descriptor; it does not create a second descriptor for the same source file.

Supported roles:

- `template` — rendered through its detected engine;
- `barrel` — authored template receiving planned exports;
- `static` — copied without rendering;
- `partial` — available to templates and never emitted;
- `documentation` — pack documentation, not generated output unless explicitly configured;
- `binary` — copied byte-for-byte.

Typical fields:

- stable ID;
- role;
- explicit target or engine only when inference is ambiguous;
- selection or aggregate scope;
- output expression;
- binding usage;
- template includes;
- providers and requirements;
- local target rules;
- conditions;
- lifecycle;
- named outputs;
- profiles.

### `profiles`

Named selections of file descriptors and option defaults. Profiles control pack shape such as modular versus monolithic generation. They never select a single language.

### `dependencies`

Desired host or owned-manifest dependencies using typed ecosystem schemas. Dependency declaration is separate from executing an installer.

### `setup`

Public configuration experience:

- summary and documentation;
- typed questions mapped to options and bindings;
- detection hints;
- typed before/after actions;
- manual steps;
- readiness messages.

`codepotg configure` interprets this contract and stores project answers in `codepotg.yaml`.

### `commands`

Pack-owned commands or typed actions. They are inspectable and subject to downloaded-pack approval policy. Templates cannot invoke commands.

### `overridePolicy`

Restricts which technically overridable adapter, engine, file, option, or binding fields the project may change. A pack can tighten but not weaken adapter or host restrictions.

## File discovery and classification

For every content root:

1. walk files deterministically;
2. apply Gitignore-compatible exclusions;
3. create one descriptor per remaining source file;
4. detect the template engine from the final registered suffix;
5. detect the target syntax from the preceding registered suffix;
6. classify non-template files as static text or binary by default;
7. apply file patterns;
8. apply exact file configuration;
9. validate explicit target/engine declarations against detected values;
10. compile selections and outputs.

## Barrel rule

A barrel is always an authored template file. The planner provides export descriptors, dependency order, and import paths. The template controls comments, headers, custom text, export syntax, side-effect imports, and formatting.

## Static file rule

Static files are emitted by default because packs may need complete non-templated project assets. Static content may be copied once or repeated through a selection/folder pattern. Its destination may be dynamic while its bytes remain unchanged.

## Command rule

A pack may polish its own output with approved actions such as formatter, linter, unused-import repair, dependency resolution, build runner, or type checking. Command capabilities and transaction phase must be visible before execution.

## Non-goals

`CodepotgPack.yaml` does not:

- require users to list every template in `codepotg.yaml`;
- define one global pack language;
- use a separate system barrel subsystem;
- hide commands inside templates;
- overwrite user-owned package manifests through raw templates when contributions are intended;
- depend on `paths.yaml` parsing in v2.
