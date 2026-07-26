# Complete project, pack, and lock example

This example links one project to three independently authored packs using the simplified filesystem-driven design.

## Project files

```text
defytickets/
├── codepotg.yaml
├── codepotg.lock.yaml
├── openapi.yaml
├── packs/
│   └── typeorm-repositories/
└── apps/
    ├── backend/
    └── mobile/
```

## Project `codepotg.yaml`

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
    options:
      clientName: DefyTicketsClient

  flutterSdk:
    source:
      git: https://github.com/alidantech-org/codepotg-pack-flutter-sdk.git
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

The project declares each pack source directly. `input` references semantic data; `output` is the pack emission root.

## TypeORM pack manifest

```yaml
apiVersion: codepotg.dev/v2

id: alidantech/typeorm-repositories
version: 1.0.0
description: Generates TypeORM entities and repositories.

requires:
  codepotg: ">=2.0 <3.0"

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
    symbols: [(entity.name.pascal.s)Repository]

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
```

Pack filesystem:

```text
templates/
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

For `OrderItem`, the repository template emits relative to the pack output root:

```text
src/repositories/order-item.repository.ts
```

The `repositories` import registry explicitly says generated entity dependencies come from the `entities` selection. `repositoriesIndex` receives the emitted repository paths and symbols and writes its own export syntax.

## TypeScript SDK pack summary

```yaml
selections:
  enums:
    paths: [src, types, enums]
    select: schemas.enums.each
    symbols: [(enum.name.pascal.s)]

  dtos:
    paths: [src, types, dtos]
    select: schemas.dtos.each
    imports:
      enums: enums
    symbols: [(dto.name.pascal.s)]

  models:
    paths: [src, types, models]
    select: schemas.models.each
    imports:
      enums: enums
    symbols: [(model.name.pascal.s)]

  typesIndex:
    paths: [src, types]
    exports: [enums, dtos, models]

  services:
    paths: [src, services]
    select: resources.each
    imports:
      types: typesIndex
    symbols: [(resource.name.pascal.s)Service]

  servicesIndex:
    paths: [src, services]
    exports: [services]

  client:
    paths: [src]
    imports:
      services: servicesIndex
    symbols: [(option.clientName)]

  rootIndex:
    paths: [src]
    exports: [typesIndex, servicesIndex, client]
```

The service selection imports required symbols through one types barrel when possible. The resolver uses declared symbols and scope; the TypeScript adapter produces the final import statements.

## Flutter SDK pack summary

```yaml
selections:
  enums:
    paths: [lib, src, models]
    select: schemas.enums.each
    symbols: [(enum.name.pascal.s)]

  models:
    paths: [lib, src, models]
    select: schemas.models.each
    imports:
      enums: enums
    symbols: [(model.name.pascal.s)]

  modelsIndex:
    paths: [lib, src, models]
    exports: [enums, models]

  services:
    paths: [lib, src, services]
    select: resources.each
    imports:
      models: modelsIndex
    symbols: [(resource.name.pascal.s)Service]

  servicesIndex:
    paths: [lib, src, services]
    exports: [services]

  client:
    paths: [lib, src]
    imports:
      services: servicesIndex
    symbols: [(option.clientName)]

  packageIndex:
    paths: [lib]
    exports: [modelsIndex, servicesIndex, client]
```

Flutter uses `lib` because all pack `paths` values are relative to the configured pack output root.

## Generated lock excerpt

```yaml
apiVersion: codepotg.dev/lock/v1

project: defytickets-generated

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
      git: https://github.com/alidantech-org/codepotg-packs.git
      ref: typescript-sdk/v2.4.1
      commit: 53e69ea110cf7739d54782d776be63ab46dfe243
      path: packs/typescript-sdk
    pack:
      id: alidantech/typescript-sdk
      version: 2.4.1
    contentDigest: sha256:4444444444444444444444444444444444444444444444444444444444444444
```

The lock keeps the requested Git ref and exact resolved commit. It stores no credentials.

## Full standalone example files

- [`../examples/project/codepotg.local.yaml`](../examples/project/codepotg.local.yaml)
- [`../examples/project/codepotg.git.yaml`](../examples/project/codepotg.git.yaml)
- [`../examples/project/codepotg.mixed.yaml`](../examples/project/codepotg.mixed.yaml)
- [`../examples/project/codepotg.lock.yaml`](../examples/project/codepotg.lock.yaml)
- [`../examples/packs/typeorm-repositories.CodepotgPack.yaml`](../examples/packs/typeorm-repositories.CodepotgPack.yaml)
- [`../examples/packs/typescript-sdk.CodepotgPack.yaml`](../examples/packs/typescript-sdk.CodepotgPack.yaml)
- [`../examples/packs/flutter-sdk.CodepotgPack.yaml`](../examples/packs/flutter-sdk.CodepotgPack.yaml)
