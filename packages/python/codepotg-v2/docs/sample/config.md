# Simplified CodepotG v2 configuration sample

This sample follows the approved human-oriented project, pack, and lock contracts.

The earlier planning draft that used `packs.<instance>.use` plus `source: api` is superseded. A pack instance now uses:

- `source` to locate the pack directly through `local` or `git`;
- `input` to reference a named semantic source;
- `output` as the pack emission root.

## Project example

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
```

## Pack example

```yaml
apiVersion: codepotg.dev/v2

id: alidantech/typeorm-repositories
version: 1.0.0
description: Generates TypeORM entities and repositories.

requires:
  codepotg: ">=2.0 <3.0"

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

Expected pack tree:

```text
templates/
├── {entities}/(entity.name.kebab.s).entity.ts.jinja
├── {repositories}/(entity.name.kebab.s).repository.ts.jinja
├── {entitiesIndex}/index.ts.jinja
├── {repositoriesIndex}/index.ts.jinja
├── {rootIndex}/index.ts.jinja
├── _partials/license.txt.jinja
├── README.md.jinja
└── .gitignore.jinja
```

## Complete maintained examples

- [`../examples/project/codepotg.local.yaml`](../examples/project/codepotg.local.yaml)
- [`../examples/project/codepotg.git.yaml`](../examples/project/codepotg.git.yaml)
- [`../examples/project/codepotg.mixed.yaml`](../examples/project/codepotg.mixed.yaml)
- [`../examples/project/codepotg.lock.yaml`](../examples/project/codepotg.lock.yaml)
- [`../examples/packs/typeorm-repositories.CodepotgPack.yaml`](../examples/packs/typeorm-repositories.CodepotgPack.yaml)
- [`../examples/packs/typescript-sdk.CodepotgPack.yaml`](../examples/packs/typescript-sdk.CodepotgPack.yaml)
- [`../examples/packs/flutter-sdk.CodepotgPack.yaml`](../examples/packs/flutter-sdk.CodepotgPack.yaml)

See the canonical specifications in:

- [`../02-configuration/01-project-config-specification.md`](../02-configuration/01-project-config-specification.md)
- [`../02-configuration/02-pack-manifest-specification.md`](../02-configuration/02-pack-manifest-specification.md)
- [`../05-distribution/02-git-github-locking-and-trust.md`](../05-distribution/02-git-github-locking-and-trust.md)
