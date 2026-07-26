# CodepotG v2 configuration examples

These files are planning fixtures for the approved human-oriented configuration design. Runtime implementation has not started.

## Project examples

- [`project/codepotg.local.yaml`](project/codepotg.local.yaml) — one local pack during pack development.
- [`project/codepotg.git.yaml`](project/codepotg.git.yaml) — one pack from a Git monorepo using URL, ref, and subdirectory.
- [`project/codepotg.mixed.yaml`](project/codepotg.mixed.yaml) — local TypeORM pack plus Git-hosted TypeScript and Flutter packs.
- [`project/codepotg.lock.yaml`](project/codepotg.lock.yaml) — generated lock for the mixed project, including exact commits and digests.

## Pack examples

- [`packs/typeorm-repositories.CodepotgPack.yaml`](packs/typeorm-repositories.CodepotgPack.yaml)
- [`packs/typescript-sdk.CodepotgPack.yaml`](packs/typescript-sdk.CodepotgPack.yaml)
- [`packs/flutter-sdk.CodepotgPack.yaml`](packs/flutter-sdk.CodepotgPack.yaml)

## Expected pack template trees

### TypeORM repositories

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

### TypeScript SDK

```text
templates/
├── {enums}/(enum.name.kebab.s).ts.jinja
├── {dtos}/(dto.name.kebab.s).dto.ts.jinja
├── {models}/(model.name.kebab.s).model.ts.jinja
├── {typesIndex}/index.ts.jinja
├── {services}/(resource.name.kebab.s).service.ts.jinja
├── {servicesIndex}/index.ts.jinja
├── {client}/(option.clientName).ts.jinja
├── {rootIndex}/index.ts.jinja
├── package.json.jinja
└── tsconfig.json
```

### Flutter SDK

```text
templates/
├── {enums}/(enum.name.snake.s).dart.jinja
├── {models}/(model.name.snake.s).dart.jinja
├── {modelsIndex}/models.dart.jinja
├── {services}/(resource.name.snake.s)_service.dart.jinja
├── {servicesIndex}/services.dart.jinja
├── {client}/(option.clientName.snake.o).dart.jinja
├── {packageIndex}/defytickets_sdk.dart.jinja
├── pubspec.yaml.jinja
└── analysis_options.yaml
```

## Design rules demonstrated

- pack instances carry direct `source.local` or `source.git` configuration;
- semantic source references use `input`;
- output paths are relative to each pack instance's `output` root;
- only `{selectionKey}` folders require manifest registration;
- `(expression)` resolves names and `((value))` emits literal parentheses;
- ordinary templates/static files are discovered automatically;
- imports and exports reference selection keys directly;
- symbols are explicit;
- command arguments are exact opaque values authored by the pack/project;
- the lock stores immutable resolution and no credentials.

The YAML files were parsed successfully during the documentation update. Future schema/conformance tests must load these exact fixtures.
