# `CodepotgPack.yaml` pack specification

## Purpose

`CodepotgPack.yaml` registers only pack behavior that cannot be inferred safely from the pack filesystem.

The filesystem defines literal templates, static files, partials, and their relative layout. The manifest defines identity, compatibility, options, bindings, selection folders, generated dependencies, symbols, executable defaults, and exact commands.

The pack consumes the closed semantic kernel defined in `../00-governance/04-closed-semantic-kernel.md`. It cannot add semantic objects, facets, selectors, expression roots, or template-context properties.

## Canonical shape

```yaml
apiVersion: codepotg.dev/v2

id: alidantech/typeorm-repositories
version: 1.0.0
description: Generates TypeORM persistence classes and repositories.

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
    description: Base class referenced by generated repository templates.

selections:
  persistenceTypes:
    paths: [src, persistence]
    select: groups.storage.mappings.each
    symbols:
      - (mapping.schema.name.pascal.s)Entity

  repositories:
    paths: [src, repositories]
    select: groups.storage.mappings.each
    imports:
      persistenceType: persistenceTypes
    bindings: [baseRepository]
    symbols:
      - (mapping.schema.name.pascal.s)Repository

  persistenceIndex:
    paths: [src, persistence]
    exports: [persistenceTypes]

  repositoriesIndex:
    paths: [src, repositories]
    exports: [repositories]

  rootIndex:
    paths: [src]
    exports: [persistenceIndex, repositoriesIndex]

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
    ├── {persistenceTypes}/
    │   └── (mapping.schema.name.kebab.s).entity.ts.jinja
    ├── {repositories}/
    │   └── (mapping.schema.name.kebab.s).repository.ts.jinja
    ├── {persistenceIndex}/
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

The template may generate a class whose name ends in `Entity`, but `entity` is template/output vocabulary. The selected neutral semantic object is a storage mapping.

## Root fields

### `apiVersion`

Required typed schema version. Initial value: `codepotg.dev/v2`.

### `id`, `version`, `description`

Pack identity and human description live at the root. `kind` and `metadata` nesting are unnecessary because the filename and schema already identify the document.

### `requires`

Compatibility requirements for CodepotG, the semantic-kernel/IR behavior, and later stable adapter contracts. Compatibility is checked before planning.

### `include` and `exclude`

Optional Gitignore-style discovery filters relative to `templates/`.

Discovery also respects the pack-root `.gitignore`. Control `.gitignore` files are not emitted. To generate one, author `.gitignore.jinja` under `templates/`.

The default content root is `templates/`; a separate `content.root` field is not required.

### `options`

Public typed pack options. Compact common forms remain readable:

```yaml
options:
  repositoryStyle:
    choices: [class, functions]
    default: class
```

The typed schema may support strings, numbers, booleans, choices, lists, mappings, paths, validation, descriptions, and examples without requiring every option to repeat a verbose `type` when its shape is unambiguous.

### `bindings`

Public project-provided values required by the pack:

```yaml
bindings:
  baseRepository:
    required: true
    description: Base class referenced by repository templates.
```

A selection lists the bindings it consumes:

```yaml
bindings: [baseRepository]
```

Project values are validated by the matching binding and target-path capability contracts. Bindings do not authorize templates to read arbitrary project files or environment values.

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
templates/{repositories}/(mapping.schema.name.kebab.s).repository.ts.jinja
```

The folder itself is replaced by the selection's `paths` array. `{root}` is built in and contributes no path segments.

Unknown selection-folder keys are errors. Literal folders do not use braces.

## `selections`

`selections` is the only explicit emission registry:

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
- one aggregate semantic file;
- one project/pack-level template;
- a barrel exporting other selections;
- a scoped barrel when its fixed selector supplies the scope.

### `paths`

Output directory relative to the pack instance's `output` root:

```yaml
paths: [src, repositories]
```

### `select`

`select` uses the fixed, versioned, root-first selector registry.

Preferred examples:

```yaml
select: groups.each
select: groups.schemas.each
select: groups.schemas.objects.each
select: groups.schemas.enums.each
select: groups.schemas.dtos.each
select: groups.operations.each
select: groups.operations.inputs.each
select: groups.operations.outputs.each
select: groups.operations.failures.each
select: groups.views.each
select: groups.storage.mappings.each
select: groups.workflows.each
select: groups.policies.each
select: groups.events.each
```

Inside an already active group selection folder, a child selection begins with the singular parent context:

```yaml
select: group.operations.each
select: group.storage.mappings.each
select: group.workflows.each
```

`.each` repeats and exposes the known singular item. `.all` emits once with the known collection. An inline alias is optional:

```yaml
select: groups.operations.each(apiOperation)
```

Aliases may not shadow active contexts.

Global selectors such as `operations.each` or `schemas.all` may be present for genuine project-wide indexes and reports, but ordinary generation should use group-rooted selectors. Packs must not select globally and reconstruct group ownership manually.

The registry does not contain:

```text
resources.each
entities.each
schemas.models.each
resource.operations.each
http.groups.each
events.operations.each
```

Packs cannot author arbitrary `where`, `traverse`, `depth`, `from`, `as`, or graph-query syntax. A recurring need becomes a named kernel selector through an IR/selection behavior version.

### Context roots

A selector establishes documented immutable context roots such as:

```text
group
schema
operation
input
output
failure
view
mapping
workflow
step
policy
event
```

Context paths follow outer-to-inner order. For example:

```text
group.operations
operation.facets.http
mapping.schema
workflow.steps
step.compensation.operation
```

Packs cannot add context roots or properties.

### `imports`

`imports` declares generated dependencies:

```yaml
imports:
  persistenceType: persistenceTypes
  sharedTypes: typesIndex
```

The mapping is `localName: selectionKey`.

Rules:

- every generated cross-selection dependency must be declared;
- undeclared required symbols are errors;
- unknown selection keys are errors;
- conflicting providers are errors;
- the resolver matches provider artifacts by semantic identity, selection scope, and declared symbols;
- the resolver supplies only the required provider artifacts and symbols;
- `.each`, `.all`, active parent scope, and barrel selections determine whether resolution produces one or several module descriptors;
- CodepotG resolves destination-relative and target-aware module/path facts before rendering;
- templates receive immutable descriptors under the declared local names and author all import syntax.

A TypeScript template might author:

```jinja
{% for module in imports.persistenceType.modules %}
import { {{ module.symbols | join(", ") }} } from "{{ module.specifier }}";
{% endfor %}
```

A Dart, Java, Rust, Python, C#, or documentation template may use the same dependency facts with completely different authored syntax. Language adapters do not inject statements.

### `exports`

Ordered selection keys exported by an authored barrel or aggregate template:

```yaml
exports: [enums, schemaTypes, repositoriesIndex]
```

A selection with `exports` waits for those emissions to be planned. Its template receives emitted paths, module/path facts, selected semantic identities, and declared symbols. It controls wildcard versus explicit exports, type-only syntax, comments, formatting, and order.

A barrel may export another barrel. Missing keys and cycles are errors.

### `symbols`

Explicit symbols emitted by each generated file:

```yaml
symbols:
  - (mapping.schema.name.pascal.s)Repository
```

CodepotG does not parse rendered code to guess exports. Symbols are used by dependency matching, barrels, conflict validation, plan inspection, and impact reporting.

### `bindings`

Names of public external bindings consumed by the selection. External project bindings remain distinct from generated selection dependencies.

## Path and filename expressions

One syntax is used for dynamic values:

```text
(group.name.path.original)
(schema.name.kebab.singular)
(operation.name.camel.original)
(mapping.schema.name.pascal.singular)
(option.clientName)
```

The naming order is always:

```text
x.name.{casing}.{number}
```

Short number aliases `o`, `s`, and `p` are allowed.

Double parentheses escape literal parentheses:

```text
((admin)) -> (admin)
```

Square brackets remain literal for framework paths.

Semantic records do not expose `fileName`, `filePath`, `directory`, or language-owned class/property-name conveniences.

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

Arguments are opaque. Core does not convert dependency declarations into package-manager syntax. Downloaded pack commands require approval by default.

## Removed or prohibited sections

The contract does not require separate root sections for:

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
facetModules
semanticExtensions
selectorQueries
```

Their useful behavior is inferred, owned by project/host policy, expressed by selections/imports/exports/bindings/commands, or added deliberately to the kernel only after a proven requirement.

## Validation

The manifest decoder rejects:

- unknown selection folders;
- unknown or reversed-root selectors;
- arbitrary query/traversal selector structures;
- invalid aliases or parent scopes;
- missing imported/exported selection keys;
- import/export cycles;
- duplicate/conflicting symbols;
- unsafe output paths;
- unsupported expression roots/properties;
- undeclared generated dependencies;
- command references to unknown executables;
- attempts to add semantic concepts, facets, context values, or selector grammar;
- attempts to add semantic `fileName`, `filePath`, or `directory` conveniences;
- configuration that asks language adapters to author emitted syntax.
