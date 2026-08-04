# Dryv configuration examples

These files are planning fixtures for the approved closed-kernel and filesystem-driven configuration design. Runtime implementation has not started.

## Project examples

- [`project/dryv.local.yaml`](project/dryv.local.yaml) — one local pack during pack development.
- [`project/dryv.git.yaml`](project/dryv.git.yaml) — one pack from a Git monorepo using URL, ref, and subdirectory.
- [`project/dryv.mixed.yaml`](project/dryv.mixed.yaml) — local TypeORM pack plus Git-hosted TypeScript and Flutter packs.
- [`project/dryv.lock.yaml`](project/dryv.lock.yaml) — generated dependency lock for the mixed project, including exact commits and digests.

## Pack examples

- [`packs/typeorm-repositories.DryvPack.yaml`](packs/typeorm-repositories.DryvPack.yaml)
- [`packs/typescript-sdk.DryvPack.yaml`](packs/typescript-sdk.DryvPack.yaml)
- [`packs/flutter-sdk.DryvPack.yaml`](packs/flutter-sdk.DryvPack.yaml)

## Expected pack template trees

### TypeORM repositories

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

`Entity` is template-authored TypeORM vocabulary. The selected neutral context is `groups.storage.mappings.each` and the template receives `mapping` plus its related schema/storage facts.

### TypeScript SDK

```text
templates/
├── {enums}/(schema.name.kebab.s).ts.jinja
├── {schemaTypes}/(schema.name.kebab.s).ts.jinja
├── {typesIndex}/index.ts.jinja
├── {groupClients}/(group.name.kebab.s).client.ts.jinja
├── {clientsIndex}/index.ts.jinja
├── {client}/(option.clientName).ts.jinja
├── {rootIndex}/index.ts.jinja
├── package.json.jinja
└── tsconfig.json
```

The group-client template iterates `group.operations` and inspects operation inputs, outputs, failures, effects, and known facets. Every TypeScript type, import, export, literal, comment, and client method is authored by the templates/macros.

### Flutter SDK

```text
templates/
├── {enums}/(schema.name.snake.s).dart.jinja
├── {schemaTypes}/(schema.name.snake.s).dart.jinja
├── {typesIndex}/types.dart.jinja
├── {groupClients}/(group.name.snake.s)_client.dart.jinja
├── {clientsIndex}/clients.dart.jinja
├── {client}/(option.clientName.snake.o).dart.jinja
├── {packageIndex}/defytickets_sdk.dart.jinja
├── pubspec.yaml.jinja
└── analysis_options.yaml
```

Flutter/Dart syntax remains entirely pack-authored. The target adapter only detects/validates `.dart` output and calculates documented target-aware module/path facts.

## Design rules demonstrated

- pack instances carry direct `source.local` or `source.git` configuration;
- semantic source references use `input`;
- output paths are relative to each pack instance's `output` root;
- packs consume the closed semantic kernel and cannot add facets/selectors/context values;
- preferred selectors start from `groups` and traverse outer-to-inner;
- only `{selectionKey}` folders require manifest registration;
- `(expression)` resolves names using `x.name.{casing}.{number}` and `((value))` emits literal parentheses;
- ordinary templates/static files are discovered automatically;
- imports and exports reference selection keys directly;
- semantic provider matching, symbols, and module/path facts are planned before rendering;
- templates author all import/export and target syntax;
- command arguments are exact opaque values authored by the pack/project;
- the dependency lock stores immutable input/behavior resolution and no credentials or generated-output hashes.

The YAML files are documentation fixtures. Future schema/conformance tests must parse these exact files and verify their selectors against the closed kernel.
