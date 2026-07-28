# Complete project, pack, and lock example

This example connects one canonical Dryv contract to three independently authored packs.

## Project files

```text
defytickets/
├── dryv.yaml
├── dryv.lock.yaml
├── contract.dryv.yaml
├── packs/
│   └── typeorm-repositories/
└── apps/
    ├── backend/
    └── mobile/
```

## Project `dryv.yaml`

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
    options:
      clientName: DefyTicketsClient

  flutterSdk:
    source:
      git: https://github.com/alidantech-org/dryv-pack-flutter-sdk.git
      ref: v1.4.2
    input: contract
    output: apps/mobile
    options:
      clientName: DefyTicketsClient

commands:
  after:
    formatWorkspace:
      executable: packageManager
      arguments: [exec, prettier, --write, packages/typescript-sdk]
      optional: true
```

The project declares every pack source directly. `input` references semantic data; `output` is the pack's destination root. The project cannot add semantic concepts, facets, selectors, or template-context roots.

## Canonical contract used by every pack

```text
Contract
└── group: orders
    ├── schemas
    ├── operations
    ├── storage mappings
    ├── views
    ├── policies
    ├── events
    ├── value sources
    └── workflows
```

The contract may be authored through `dryv-author`, a future native Codepot language, or another host that returns a public `Contract`. JSON/YAML is optional transport; every route reaches the same immutable semantic representation.

The packs consume shared semantic identities while authoring different output text.

## TypeORM pack manifest

```yaml
apiVersion: dryv.dev/v1

id: alidantech/typeorm-repositories
version: 1.0.0
description: Generates TypeORM persistence classes and repositories.

requires:
  dryv: ">=2.0 <3.0"
  ir: ">=2.0 <3.0"

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
```

Pack tree:

```text
templates/
├── {persistenceTypes}/(mapping.schema.name.kebab.s).entity.ts.jinja
├── {repositories}/(mapping.schema.name.kebab.s).repository.ts.jinja
├── {persistenceIndex}/index.ts.jinja
├── {repositoriesIndex}/index.ts.jinja
├── {rootIndex}/index.ts.jinja
├── _partials/license.txt.jinja
├── README.md.jinja
└── .gitignore.jinja
```

`Entity` and `Repository` are pack-owned output vocabulary. The selected neutral object is `mapping`.

The runtime matches the repository artifact to its generated persistence type through semantic identity and selection declarations, resolves module/path facts through the TypeScript plugin, and supplies immutable descriptors to the template. The template writes the import and class text.

## TypeScript SDK pack summary

```yaml
selections:
  enums:
    paths: [src, types, enums]
    select: groups.schemas.enums.each
    symbols: [(schema.name.pascal.s)]

  schemaTypes:
    paths: [src, types, schemas]
    select: groups.schemas.objects.each
    imports:
      enums: enums
    symbols: [(schema.name.pascal.s)]

  typesIndex:
    paths: [src, types]
    exports: [enums, schemaTypes]

  groupClients:
    paths: [src, clients]
    select: groups.each
    imports:
      types: typesIndex
    symbols: [(group.name.pascal.s)Client]

  clientsIndex:
    paths: [src, clients]
    exports: [groupClients]

  client:
    paths: [src]
    imports:
      clients: clientsIndex
    symbols: [(option.clientName)]

  rootIndex:
    paths: [src]
    exports: [typesIndex, clientsIndex, client]
```

A group-client template receives `group` and its documented relationships. The pack decides whether to generate classes, functions, clients, request helpers, or documentation.

The TypeScript target plugin validates paths and module specifiers. Templates author every TypeScript type, import, export, comment, literal, and client statement.

## Dart/Flutter pack summary

```yaml
selections:
  enums:
    paths: [lib, src, types, enums]
    select: groups.schemas.enums.each
    symbols: [(schema.name.pascal.s)]

  schemaTypes:
    paths: [lib, src, types, schemas]
    select: groups.schemas.objects.each
    imports:
      enums: enums
    symbols: [(schema.name.pascal.s)]

  typesIndex:
    paths: [lib, src, types]
    exports: [enums, schemaTypes]

  groupClients:
    paths: [lib, src, clients]
    select: groups.each
    imports:
      types: typesIndex
    symbols: [(group.name.pascal.s)Client]

  clientsIndex:
    paths: [lib, src, clients]
    exports: [groupClients]

  client:
    paths: [lib, src]
    imports:
      clients: clientsIndex
    symbols: [(option.clientName)]

  packageIndex:
    paths: [lib]
    exports: [typesIndex, clientsIndex, client]
```

Flutter policy remains pack-owned. The Dart target plugin supplies validation and URI facts only. Templates author every class, import, export, annotation, serialization expression, widget, navigation rule, and client call.

## Connected-generation behavior

One semantic identity may drive many artifacts without sharing filenames or target syntax:

```text
schema: Order
├── TypeScript type
├── Dart type
├── storage type
├── repository
├── group client methods
└── documentation
```

Changing a schema or operation lets the planner report affected selectors and artifacts before writing. The dependency graph is semantic; all generated text remains pack-authored.

## Lock excerpt

```yaml
apiVersion: dryv.dev/lock/v1

project: defytickets-generated

runtime:
  dryv: 2.0.0
  ir: 2.0
  namingBehavior: 1
  selectionBehavior: 1

packs:
  backendRepositories:
    source:
      local: ./packs/typeorm-repositories
    pack:
      id: alidantech/typeorm-repositories
      version: 1.0.0
    contentDigest: sha256:2222222222222222222222222222222222222222222222222222222222222222

  typescriptSdk:
    source:
      git: https://github.com/alidantech-org/dryv-packs.git
      ref: typescript-sdk/v2.4.1
      commit: 53e69ea110cf7739d54782d776be63ab46dfe243
      path: packs/typescript-sdk
    pack:
      id: alidantech/typescript-sdk
      version: 2.4.1
    contentDigest: sha256:4444444444444444444444444444444444444444444444444444444444444444

plugins:
  source.ir:
    package: dryv
    version: 2.0.0
    behavior: 1
```

The lock stores requested refs, exact resolved commits, pack/plugin versions, and behavior identity. It stores no credentials and no generated output hashes. Output hashes belong to `.dryv/generation-state.json`.

## Standalone examples

- [`../examples/project/dryv.local.yaml`](../examples/project/dryv.local.yaml)
- [`../examples/project/dryv.git.yaml`](../examples/project/dryv.git.yaml)
- [`../examples/project/dryv.mixed.yaml`](../examples/project/dryv.mixed.yaml)
- [`../examples/project/dryv.lock.yaml`](../examples/project/dryv.lock.yaml)
- [`../examples/packs/typeorm-repositories.DryvPack.yaml`](../examples/packs/typeorm-repositories.DryvPack.yaml)
- [`../examples/packs/typescript-sdk.DryvPack.yaml`](../examples/packs/typescript-sdk.DryvPack.yaml)
- [`../examples/packs/flutter-sdk.DryvPack.yaml`](../examples/packs/flutter-sdk.DryvPack.yaml)
