# Dryv configuration sample

This sample shows one canonical semantic contract driving several packs.

A pack instance uses:

- `source` to locate the pack through `local` or `git`;
- `input` to reference a named semantic contract;
- `output` as its destination root;
- `options` and `bindings` for explicitly declared pack configuration.

## Project example

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

  flutterSdk:
    source:
      git: https://github.com/alidantech-org/dryv-pack-flutter-sdk.git
      ref: v1.4.2
    input: contract
    output: apps/mobile
```

## Pack example

```yaml
apiVersion: dryv.dev/v1

id: alidantech/typescript-models
version: 1.0.0
description: Generates TypeScript models and repository files.

requires:
  dryv: ">=2.0 <3.0"

bindings:
  baseRepository:
    required: true
    description: Base class imported by generated repositories.

selections:
  models:
    paths: [src, models]
    select: groups.schemas.objects.each
    symbols: [(schema.name.pascal.s)]

  repositories:
    paths: [src, repositories]
    select: groups.schemas.objects.each
    imports:
      models: models
    bindings: [baseRepository]
    symbols: [(schema.name.pascal.s)Repository]

  modelsIndex:
    paths: [src, models]
    exports: [models]

  repositoriesIndex:
    paths: [src, repositories]
    exports: [repositories]

  rootIndex:
    paths: [src]
    exports: [modelsIndex, repositoriesIndex]

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
├── {models}/(schema.name.kebab.s).ts.jinja
├── {repositories}/(schema.name.kebab.s).repository.ts.jinja
├── {modelsIndex}/index.ts.jinja
├── {repositoriesIndex}/index.ts.jinja
├── {rootIndex}/index.ts.jinja
├── _partials/license.txt.jinja
├── README.md.jinja
└── .gitignore.jinja
```

## Maintained examples

- [`../examples/project/dryv.local.yaml`](../examples/project/dryv.local.yaml)
- [`../examples/project/dryv.git.yaml`](../examples/project/dryv.git.yaml)
- [`../examples/project/dryv.mixed.yaml`](../examples/project/dryv.mixed.yaml)
- [`../examples/project/dryv.lock.yaml`](../examples/project/dryv.lock.yaml)
- [`../examples/packs/typeorm-repositories.DryvPack.yaml`](../examples/packs/typeorm-repositories.DryvPack.yaml)
- [`../examples/packs/typescript-sdk.DryvPack.yaml`](../examples/packs/typescript-sdk.DryvPack.yaml)
- [`../examples/packs/flutter-sdk.DryvPack.yaml`](../examples/packs/flutter-sdk.DryvPack.yaml)

See:

- [`../02-configuration/01-project-config-specification.md`](../02-configuration/01-project-config-specification.md)
- [`../02-configuration/02-pack-manifest-specification.md`](../02-configuration/02-pack-manifest-specification.md)
- [`../05-distribution/02-git-github-locking-and-trust.md`](../05-distribution/02-git-github-locking-and-trust.md)
