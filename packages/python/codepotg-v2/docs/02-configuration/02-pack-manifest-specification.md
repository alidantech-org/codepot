# `CodepotgPack.yaml` pack specification

## Purpose

`CodepotgPack.yaml` registers only pack behavior that cannot be inferred safely from the pack filesystem.

The filesystem defines literal templates, static files, partials, and their relative layout. The manifest defines identity, compatibility, options, bindings, selection folders, generated dependencies, symbols, executable defaults, and exact lifecycle commands.

## Canonical shape

```yaml
apiVersion: codepotg.dev/v2

id: alidantech/typeorm-repositories
version: 1.0.0
description: Generates TypeORM entities and repositories.

requires:
  codepotg: ">=2.0 <3.0"
  ir: ">=2.0 <3.0"

include:
  - "**/*"

exclude:
  - _authoring/**
  - "**/*.draft"

options:
  repositoryStyle:
    choices: [class, functions]
    default: class

bindings:
  baseRepository:
    required: true
    description: Base class imported by generated repositories.

selections:
  entities:
    paths: [src, entities]
    select: entities.each
    symbols: [(entity.name.pascal.s)]

  repositories:
    paths: [src, repositories]
    select: entities.each
    imports:
      entities: entities
    bindings: [baseRepository]
    symbols:
      - (entity.name.pascal.s)Repository

  entitiesIndex:
    paths: [src, entities]
    exports: [entities]

  repositoriesIndex:
    paths: [src, repositories]
    exports: [repositories]

  rootIndex:
    paths: [src]
    exports: [entitiesIndex, repositoriesIndex]

executables:
  packageManager: pnpm

commands:
  after:
    install:
      executable: packageManager
      arguments: [add, typeorm@^0.3.0, reflect-metadata@^0.2.0]

    format:
      executable: packageManager
      arguments: [exec, prettier, --write, src]
      optional: true
```

## Corresponding filesystem

```text
typeorm-repositories/
├── CodepotgPack.yaml
├── .gitignore
├── docs/
└── templates/
    ├── {entities}/
    │   └── (entity.name.kebab.s).entity.ts.jinja
    ├── {repositories}/
    │   └── (entity.name.kebab.s).repository.ts.jinja
    ├── {entitiesIndex}/
    │   └── index.ts.jinja
    ├── {repositoriesIndex}/
    │   └── index.ts.jinja
    ├── {rootIndex}/
    │   └── index.ts.jinja
    ├── _partials/
    │   └── license.txt.jinja
    ├── README.md.jinja
    └── .gitignore.jinja
```

## Root fields

### `apiVersion`

Required typed schema version. Initial value: `codepotg.dev/v2`.

### `id`, `version`, `description`

Pack identity and human description live at the root. `kind` and `metadata` nesting are unnecessary because the filename and schema already identify the document.

Optional documentation fields such as repository, license, homepage, authors, tags, and docs path may be added as direct metadata fields when required.

### `requires`

Compatibility requirements for CodepotG, IR, and later stable adapter contracts. Compatibility is checked before planning.

### `include` and `exclude`

Optional Gitignore-style discovery filters relative to `templates/`.

Discovery also respects the pack-root `.gitignore`. Control `.gitignore` files are not emitted. To generate a `.gitignore`, author `.gitignore.jinja` under `templates/`.

The default content root is `templates/`; a separate `content.root` field is not required.

### `options`

Public typed pack options. Compact common forms should stay readable:

```yaml
options:
  repositoryStyle:
    choices: [class, functions]
    default: class
```

The typed schema may support strings, numbers, booleans, choices, lists, mappings, paths, validation, descriptions, and examples without requiring every option to repeat a verbose `type` when its shape is unambiguous.

### `bindings`

Public project-provided values required by the pack.

```yaml
bindings:
  baseRepository:
    required: true
    description: Base class used by generated repositories.
```

A selection lists the bindings it consumes:

```yaml
bindings: [baseRepository]
```

Project values are validated by the matching binding and language contracts.

## Filesystem discovery

### Literal templates

A literal template is rendered at its literal pack-relative location and loses only the recognized engine suffix:

```text
templates/package.json.jinja -> package.json
templates/src/config.ts.jinja -> src/config.ts
```

Literal templates do not require manifest entries.

### Static and binary files

Non-template files are copied unchanged at the same relative location:

```text
templates/assets/logo.png -> assets/logo.png
templates/analysis_options.yaml -> analysis_options.yaml
```

Static and binary files do not require manifest entries.

### Partials

`templates/_partials/**` is available to template engines and is never emitted.

### Selection folders

A whole folder segment wrapped in braces references a registered selection key:

```text
templates/{repositories}/(entity.name.kebab.s).repository.ts.jinja
```

The folder itself is replaced by the selection's `paths` array.

`{root}` is built in and contributes no path segments.

Unknown selection-folder keys are errors. Literal folders do not use braces.

## `selections`

`selections` is the only explicit emission registry.

```yaml
selections:
  selectionKey:
    paths: [relative, output, directory]
    select: optional.fixed.selector
    imports:
      localName: anotherSelectionKey
    exports: [selectionKey]
    bindings: [bindingKey]
    symbols: [(typed.expression)]
```

A selection may represent:

- repeated source-driven files;
- one aggregate file;
- one project/pack-level template;
- a barrel exporting other selections;
- a scoped barrel when its fixed selector supplies the scope.

### `paths`

Output directory relative to the pack instance's `output` root.

```yaml
paths: [src, repositories]
```

Short paths use a one-line YAML sequence. Multiline YAML sequences remain equivalent when readability requires them.

### `select`

Uses the fixed selector registry:

```yaml
select: entities.each
select: schemas.dtos.all
select: resources.each(apiResource)
```

`.each` repeats and exposes the known singular item. `.all` emits once with the collection. An inline alias is optional.

Initial fixed selectors include:

```text
resources.each / resources.all
entities.each / entities.all
schemas.each / schemas.all
schemas.models.each / schemas.models.all
schemas.dtos.each / schemas.dtos.all
schemas.enums.each / schemas.enums.all
operations.each / operations.all
resource.entities.each / resource.entities.all
resource.schemas.each / resource.schemas.all
resource.operations.each / resource.operations.all
entity.fields.each / entity.fields.all
schema.properties.each / schema.properties.all
operation.parameters.each / operation.parameters.all
operation.responses.each / operation.responses.all
enum.members.each / enum.members.all
```

The registry is versioned and introspectable. Packs cannot invent arbitrary `from`/`as` traversal in YAML.

### `imports`

Explicit generated dependency registry:

```yaml
imports:
  entities: entities
  types: typesIndex
```

The mapping is `localName: selectionKey`.

Rules:

- every generated cross-selection dependency must be declared;
- undeclared required symbols are errors;
- unknown selection keys are errors;
- conflicting providers are errors;
- the resolver imports only the least required symbols;
- `.each`, `.all`, parent scope, and barrel selections determine whether resolution produces one or several modules;
- language adapters produce final import syntax and module paths;
- templates receive the prepared import plan under the declared local names.

### `exports`

Ordered selection keys exported by an authored barrel or aggregate template:

```yaml
exports: [enums, dtos, repositoriesIndex]
```

A selection with `exports` waits for those emissions to be planned. Its template receives each emitted path and its declared symbols and controls:

- wildcard versus explicit exports;
- type-only exports;
- comments and formatting;
- order within each exported group.

A barrel may export another barrel. Missing keys and cycles are errors.

### `symbols`

Explicit symbols emitted by each generated file:

```yaml
symbols:
  - (entity.name.pascal.s)Repository
```

CodepotG does not parse rendered code to guess exports. Symbols are used by imports, barrels, conflicts, and plan inspection.

### `bindings`

Names of public external bindings consumed by the selection.

## Path and filename expressions

One syntax is used for dynamic values:

```text
(entity.name.kebab.s)
(resource.name.path.o)
(option.clientName)
```

Double parentheses escape literal parentheses:

```text
((admin)) -> (admin)
```

Square brackets remain literal for framework paths.

See [`../03-generation/00-path-expressions-and-name-tokens.md`](../03-generation/00-path-expressions-and-name-tokens.md).

## `executables`

Pack-provided defaults:

```yaml
executables:
  packageManager: pnpm
```

The project may replace them globally or per pack instance. A command references the key through `executable`.

## `commands`

Pack-owned exact before/after commands:

```yaml
commands:
  after:
    install:
      executable: packageManager
      arguments: [add, typeorm@^0.3.0]
```

Arguments are opaque. Core does not convert dependency declarations into package-manager syntax. Packs may set themselves up through approved commands; projects may replace executable names/paths or disable/override commands through typed project configuration.

Downloaded pack commands require approval by default.

## Removed redundant sections

The simplified contract does not require separate root sections for:

```text
kind
metadata
integration
content.root
writePolicy
languages
templateEngines
paths
filePatterns
files
profiles
dependencies
setup.actions
overridePolicy
```

Their useful behavior is either inferred from the filesystem, owned by adapters/project policy, expressed by selections/imports/exports/bindings/commands, or deferred until a real pack proves a smaller explicit field is required.

## Validation

The manifest decoder rejects:

- unknown selection folders;
- unknown fixed selectors;
- invalid aliases;
- missing imported/exported selection keys;
- import/export cycles;
- duplicate/conflicting symbols;
- unsafe output paths;
- unsupported expressions;
- undeclared generated dependencies;
- command references to unknown executables;
- attempts to add semantic `fileName`, `filePath`, or `directory` conveniences.
