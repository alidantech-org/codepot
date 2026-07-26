# `CodepotgPack.yaml` pack specification

## Purpose

`CodepotgPack.yaml` is the complete authored contract for one template pack. It replaces the conceptual responsibility previously associated with `paths.yaml`, but v2 does not implement a `paths.yaml` compatibility decoder.

The pack manifest describes how the pack discovers source files, composes their output paths, selects data, declares bindings and dependencies, applies language/engine rules, exposes setup, and performs approved lifecycle actions.

A pack may create a complete runnable project, a standalone package folder, an extension to an existing project, fragments requiring user integration, or any combination of those traits.

## Critical path rule

The relative source path below the content root is the default output-path program.

```text
templates/{repositories}/[entity.name.kebab.s].repository.ts.jinja
```

may emit:

```text
src/repositories/order.repository.ts
```

The pack composes this through named `paths` recipes and typed `[expression]` tokens. Semantic records do not expose invented `fileName` or `directory` properties.

See [`../03-generation/00-path-expressions-and-name-tokens.md`](../03-generation/00-path-expressions-and-name-tokens.md).

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
    orderBy: name

paths:
  repositories:
    selection:
      use: entities
    parts:
      - src
      - repositories

  repositoriesRoot:
    parts:
      - src
      - repositories

  projectRoot:
    parts: []

filePatterns:
  "**/*.spec.ts.jinja":
    profiles: [tests]

  "_partials/**/*.jinja":
    role: partial

files:
  "{repositories}/[entity.name.kebab.s].repository.ts.jinja":
    id: repository
    role: template
    uses:
      bindings: [baseRepository]
    provides:
      - repository.entity

  "{repositoriesRoot}/index.ts.jinja":
    id: repositoryIndex
    role: barrel
    selection:
      scope: aggregate
    exports:
      include: [repository]

  "_partials/license.txt.jinja":
    id: licenseHeader
    role: partial
    target: plainText

  "{projectRoot}/.gitignore":
    id: generatedIgnore
    role: static

profiles:
  modular:
    enable: [repository, repositoryIndex, generatedIgnore]

  tests:
    enable: [repository, repositoryIndex, generatedIgnore]

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
      paths: ["{output.root}/src/repositories/**/*.{ts,tsx}"]
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

Required typed schema version. Initial value: `codepotg.dev/v2`.

### `kind`

Required and exactly `TemplatePack`.

### `metadata`

Pack identity and documentation metadata:

- globally meaningful ID;
- semantic version;
- description;
- optional authors, license, repository, homepage, tags, and documentation path.

### `compatibility`

Compatibility with core, plugin API, IR, target adapters, engines, ecosystem adapters, and optional capabilities. Compatibility is checked before planning.

### `integration`

Composable traits describing how the pack participates in a host project. Traits are descriptive and combinable; they are not one restrictive enum.

### `content`

Content roots and ignore behavior:

- `root` or multiple named roots;
- inline Gitignore-compatible `ignore` patterns;
- optional `ignoreFile`, normally `.codepotgignore`;
- deterministic discovery order.

Pack metadata, Git internals, caches, tasks, and authoring docs are not emitted unless intentionally placed below a content root.

### `writePolicy`

Pack lifecycle intent:

- default managed, immutable, protected, or unmanaged mode;
- suggested managed roots;
- protected paths;
- ownership metadata.

The project and host retain authority over destructive cleanup.

### `options`

Public typed pack options. Supported schemas include string, integer, number, boolean, enum, path, list, typed mapping, and structured object.

Each option may declare required state, default, validation, description, examples, and configure prompt metadata.

### `languages`

Rules for every target syntax used by the pack. This is a mapping, not one selected language.

Each language adapter decodes its own typed section. A heterogeneous pack may contain TypeScript, Dart, Markdown, YAML, SQL, JSON, Dockerfiles, and other targets together.

### `templateEngines`

Typed engine rules for engines used by discovered templates. Security-sensitive fields remain host-controlled.

### `bindings`

The public binding catalog. Each binding defines:

- meaning and type;
- target when applicable;
- required/optional state;
- accepted project sources;
- discovery hints;
- missing behavior;
- documentation and examples.

Individual files list consumed binding IDs under `uses.bindings`.

### `selections`

Named typed selections over neutral IR or already planned artifacts. A selection declares collection, alias, filter, ordering, grouping, aggregation, or artifact projection.

Selections are evaluated by the planner, never by template code.

### `paths`

Reusable named path recipes.

A recipe may declare:

- optional selection or named-selection reference;
- alias introduced by that selection;
- zero or more typed destination parts;
- optional lifecycle defaults;
- optional documentation.

A recipe is referenced in a source path with `{recipe}`.

```yaml
paths:
  resource:
    selection:
      each: resources
      as: resource
    parts:
      - gen
      - server
      - "[resource.path]"
      - "[resource.name.path.o]"
```

A source file can compose several recipes:

```text
{resource}/{entity}/[entity.name.kebab.s].entity.ts.jinja
```

Recipes are evaluated left to right. Later recipes may use aliases introduced by earlier recipes.

### `filePatterns`

Defaults for matching discovered source descriptors. Typical uses include:

- classify `_partials/**` as partials;
- add profile membership to test templates;
- apply local rules or lifecycle defaults;
- declare common bindings or requirements.

`filePatterns` should not be the primary way to manufacture output roots. The source path and named `paths` recipes own normal destination composition.

Pattern precedence is deterministic: broad patterns, more specific patterns, exact `files` entry.

### `files`

Exact configuration for discovered pack files. An entry modifies one descriptor and does not create another emission.

Supported roles:

- `template`;
- `barrel`;
- `static`;
- `binary`;
- `partial`;
- `documentation`.

Typical fields:

- stable ID;
- role;
- explicit target/engine only when inference is ambiguous;
- selection when not introduced by a path recipe;
- binding usage;
- includes;
- providers and requirements;
- local target/engine rules;
- conditions;
- lifecycle;
- profile membership;
- authored barrel export requirements;
- exceptional output override;
- multiple predeclared named outputs.

The key is the actual content-root-relative source path, including tokens:

```yaml
files:
  "{models}/[model.name.pascal.s].model.ts.jinja":
    id: model
    role: template
```

### `profiles`

Named sets of source descriptors and option defaults. Profiles may choose modular, grouped, monolithic, tests, examples, or framework variants. They never select one pack language.

### `dependencies`

Desired host or owned-manifest dependencies using typed ecosystem schemas. Dependency declarations are separate from installer execution.

### `setup`

Public configuration experience:

- summary and documentation;
- typed questions mapped to options and bindings;
- discovery hints;
- typed before/after actions;
- manual steps;
- readiness messages.

`codepotg configure` interprets this contract and stores answers under the matching pack instance in `codepotg.yaml`.

### `commands`

Pack-owned commands and typed actions. They are inspectable and governed by downloaded-pack approval policy. Templates cannot invoke commands.

### `overridePolicy`

Restrictions on technically overridable adapter, engine, file, option, binding, and path-rule fields. A pack may tighten but never weaken adapter or host restrictions.

## File discovery and destination compilation

For every content root:

1. walk files deterministically;
2. apply Gitignore-compatible exclusions;
3. create one descriptor per remaining source file;
4. detect engine from the final registered suffix;
5. detect target from the preceding registered suffix;
6. classify non-template files as static text or binary by default;
7. apply descriptor patterns;
8. apply exact file configuration;
9. compile file selection and path-recipe selections;
10. parse source-path tokens;
11. expand recipes and typed expressions;
12. strip only the engine suffix for emitted templates;
13. preserve static/binary bytes and target suffixes;
14. validate destinations before rendering.

## Path and name rules

Stable dynamic name paths include:

```text
name.raw
name.clean
name.snake
name.kebab
name.camel
name.pascal
name.screaming
name.constant
name.dot
name.path
name.lower
name.upper
```

Each exposes `o/original`, `s/singular`, `p/plural`, and `number`.

Examples:

```text
[entity.name.kebab.s]
[resource.name.path.o]
[operation.name.camel.o]
```

No semantic record is required to expose a precomputed filename.

## Explicit output override rule

An explicit `output` is exceptional. It is used for authoring layouts that cannot express the destination naturally or for multiple named outputs.

It uses the same typed grammar:

```yaml
output:
  parts:
    - gen
    - "[project.name.kebab.o]-sdk.ts"
```

It never evaluates Jinja or arbitrary Python.

## Barrel rule

A barrel is always an authored template source file. Its filename and location use the same path recipes and tokens as other files. The planner supplies exports; the template owns comments, headers, side effects, syntax, and formatting.

## Static file rule

Static and binary files are emitted by default. Their bytes remain unchanged, but tokenized source folders may fan them out and compose their destination.

## Command rule

A pack may polish its own output with approved format, lint, unused-import repair, dependency, build-runner, validation, or typecheck actions. Ownership, phase, capabilities, and exact command digest are visible before execution.

## Non-goals

`CodepotgPack.yaml` does not:

- require users to list internal templates in `codepotg.yaml`;
- select one global pack language;
- require semantic `fileName` or `directory` fields;
- generate barrels through a hidden root subsystem;
- hide commands inside templates;
- overwrite user-owned manifests through raw templates when contributions are intended;
- parse `paths.yaml` in v2.
