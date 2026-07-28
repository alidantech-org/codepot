# Complete project, pack, and lock example

This example links one project to three independently authored packs using the closed semantic kernel and simplified filesystem-driven design.

## Project files

```text
defytickets/
├── dryv.yaml
├── dryv.lock.yaml
├── openapi.yaml
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
      git: https://github.com/alidantech-org/dryv-packs.git
      ref: typescript-sdk/v2.4.1
      path: packs/typescript-sdk
    input: api
    output: packages/typescript-sdk
    options:
      clientName: DefyTicketsClient

  flutterSdk:
    source:
      git: https://github.com/alidantech-org/dryv-pack-flutter-sdk.git
      ref: v1.4.2
    input: api
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

The project declares each pack source directly. `input` references semantic data; `output` is the pack emission root. The project cannot add semantic concepts, facets, or selectors.

## OpenAPI normalization used by all packs

The OpenAPI adapter normalizes the source into the known kernel:

```text
contract.groups
└── group: orders
    ├── schemas
    ├── operations
    ├── storage.mappings       when typed x-codegen metadata declares them
    ├── views                  when typed x-codegen metadata declares them
    ├── workflows              when typed x-codegen metadata declares them
    ├── policies
    └── events
```

HTTP paths and methods become `operation.facets.http`; operation data remains under inputs, outputs, failures, and effects. The three packs consume the same semantic identities but author different output text.

## TypeORM pack manifest

```yaml
apiVersion: dryv.dev/v1

id: alidantech/typeorm-repositories
version: 1.0.0
description: Generates TypeORM persistence classes and repositories from storage mappings.

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

Pack filesystem:

```text
templates/
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

For a mapping whose schema is `OrderItem`, the repository template may emit:

```text
src/repositories/order-item.repository.ts
```

`Entity` is authored TypeORM output vocabulary. The neutral selected object is `mapping`.

The `repositories` dependency says that the corresponding generated persistence type comes from `persistenceTypes`. Dryv matches artifacts through the same mapping/schema semantic identity, resolves symbols and path/module facts, and passes descriptors to the repository template. The template writes the TypeScript import and class code.

## TypeScript SDK pack summary

```yaml
selections:
  enums:
    paths: [src, types, enums]
    select: groups.schemas.enums.each
    symbols:
      - (schema.name.pascal.s)

  schemaTypes:
    paths: [src, types, schemas]
    select: groups.schemas.objects.each
    imports:
      enums: enums
    symbols:
      - (schema.name.pascal.s)

  typesIndex:
    paths: [src, types]
    exports: [enums, schemaTypes]

  groupClients:
    paths: [src, clients]
    select: groups.each
    imports:
      types: typesIndex
    symbols:
      - (group.name.pascal.s)Client

  clientsIndex:
    paths: [src, clients]
    exports: [groupClients]

  client:
    paths: [src]
    imports:
      clients: clientsIndex
    symbols:
      - (option.clientName)

  rootIndex:
    paths: [src]
    exports: [typesIndex, clientsIndex, client]
```

A `groupClients` template receives `group` and traverses `group.operations`. Each operation exposes inputs, outputs, failures, effects, and known facets. The pack decides whether to generate a class, functions, method groups, request types, or documentation.

The TypeScript target adapter validates output names and resolves target-aware module-specifier facts. The templates author all TypeScript imports, exports, types, comments, literals, and client logic.

## Flutter SDK pack summary

```yaml
selections:
  enums:
    paths: [lib, src, types, enums]
    select: groups.schemas.enums.each
    symbols:
      - (schema.name.pascal.s)

  schemaTypes:
    paths: [lib, src, types, schemas]
    select: groups.schemas.objects.each
    imports:
      enums: enums
    symbols:
      - (schema.name.pascal.s)

  typesIndex:
    paths: [lib, src, types]
    exports: [enums, schemaTypes]

  groupClients:
    paths: [lib, src, clients]
    select: groups.each
    imports:
      types: typesIndex
    symbols:
      - (group.name.pascal.s)Client

  clientsIndex:
    paths: [lib, src, clients]
    exports: [groupClients]

  client:
    paths: [lib, src]
    imports:
      clients: clientsIndex
    symbols:
      - (option.clientName)

  packageIndex:
    paths: [lib]
    exports: [typesIndex, clientsIndex, client]
```

Flutter uses `lib` because all pack `paths` values are relative to the configured pack output root. The Dart/Flutter templates author every class, import, export, annotation, serialization expression, and client call.

A separate Flutter application pack may select `groups.views.each` when the semantic input actually contains known view declarations. The SDK pack does not invent views from HTTP operations.

## Connected-generation behavior

All three packs can depend on one semantic schema identity without sharing filenames or target syntax:

```text
schema: Order
├── TypeScript type artifact
├── Dart type artifact
├── storage mapping artifact
├── repository artifact
├── group client methods
└── documentation artifacts
```

Changing `Order.email` or an operation that uses `Order` lets the planner report the affected selections and artifacts before writing. The dependency graph is semantic, while all generated text remains pack-authored.

## Generated lock excerpt

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
```

The lock keeps requested Git refs, exact resolved commits, pack/plugin versions, and behavior identity. It stores no credentials and no generated output hashes. Output digests belong to the ownership/generation-state manifest.

## Full standalone example files

- [`../examples/project/dryv.local.yaml`](../examples/project/dryv.local.yaml)
- [`../examples/project/dryv.git.yaml`](../examples/project/dryv.git.yaml)
- [`../examples/project/dryv.mixed.yaml`](../examples/project/dryv.mixed.yaml)
- [`../examples/project/dryv.lock.yaml`](../examples/project/dryv.lock.yaml)
- [`../examples/packs/typeorm-repositories.DryvPack.yaml`](../examples/packs/typeorm-repositories.DryvPack.yaml)
- [`../examples/packs/typescript-sdk.DryvPack.yaml`](../examples/packs/typescript-sdk.DryvPack.yaml)
- [`../examples/packs/flutter-sdk.DryvPack.yaml`](../examples/packs/flutter-sdk.DryvPack.yaml)
