Below is a compact **planning draft** using the decisions made so far:

* one project-owned `codepotg.yaml`;
* three filesystem-driven packs;
* only selections are registered;
* ordinary templates and static files are discovered automatically;
* `{selectionKey}` connects folders to selections;
* `(expression)` resolves names;
* `imports` and `exports` connect selections;
* commands contain exact executable arguments.

# 1. Project `codepotg.yaml`

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

packs:
  backendRepositories:
    use: ./packs/typeorm-repositories
    source: api
    output: apps/backend

    options:
      repositoryStyle: class

    bindings:
      baseRepository:
        from: src/database/base.repository
        symbol: BaseRepository

  typescriptSdk:
    use: ./packs/typescript-sdk
    source: api
    output: packages/typescript-sdk

    options:
      clientName: DefyTicketsClient

  flutterSdk:
    use: ./packs/flutter-sdk
    source: api
    output: apps/mobile

    options:
      clientName: DefyTicketsClient

commands:
  before:
    validateSource:
      executable: codepotg
      arguments: [validate, ./openapi.yaml]

  after:
    formatWorkspace:
      executable: packageManager
      arguments: [exec, prettier, --write, packages/typescript-sdk]
      optional: true
```

## Project meaning

```text
sources
```

Defines the source once.

```text
executables
```

Provides executable names or paths that packs may use.

```text
packs
```

Uses three independently authored packs.

```text
output
```

Is the emission root for that pack instance.

For example:

```yaml
output: apps/backend
```

combined with:

```yaml
paths: [src, repositories]
```

produces:

```text
apps/backend/src/repositories
```

---

# 2. TypeORM pack

## `packs/typeorm-repositories/CodepotgPack.yaml`

```yaml
apiVersion: codepotg.dev/v2

id: alidantech/typeorm-repositories
version: 1.0.0
description: Generates TypeORM entities and repositories.

requires:
  codepotg: ">=2.0 <3.0"

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
    installDependencies:
      executable: packageManager
      arguments:
        - add
        - typeorm@^0.3.0
        - reflect-metadata@^0.2.0

    format:
      executable: packageManager
      arguments:
        - exec
        - prettier
        - --write
        - src/entities
        - src/repositories
      optional: true
```

## Pack filesystem

```text
typeorm-repositories/
├── CodepotgPack.yaml
├── .gitignore
├── docs/
│   └── setup.md
└── templates/
    ├── {entities}/
    │   └── (entity.name.kebab.s).entity.ts.jinja
    │
    ├── {repositories}/
    │   └── (entity.name.kebab.s).repository.ts.jinja
    │
    ├── {entitiesIndex}/
    │   └── index.ts.jinja
    │
    ├── {repositoriesIndex}/
    │   └── index.ts.jinja
    │
    ├── {rootIndex}/
    │   └── index.ts.jinja
    │
    ├── _partials/
    │   └── license.txt.jinja
    │
    └── README.md
```

## Example generated output

```text
apps/backend/
├── README.md
└── src/
    ├── index.ts
    ├── entities/
    │   ├── index.ts
    │   ├── order.entity.ts
    │   └── customer.entity.ts
    └── repositories/
        ├── index.ts
        ├── order.repository.ts
        └── customer.repository.ts
```

The repository selection explicitly declares:

```yaml
imports:
  entities: entities
```

Therefore generated repositories may import entity symbols only through the `entities` selection.

The import resolver determines the minimum entity imports required by each repository.

---

# 3. TypeScript SDK pack

## `packs/typescript-sdk/CodepotgPack.yaml`

```yaml
apiVersion: codepotg.dev/v2

id: alidantech/typescript-sdk
version: 1.0.0
description: Generates a typed TypeScript API client.

requires:
  codepotg: ">=2.0 <3.0"

options:
  clientName:
    default: ApiClient

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

    symbols:
      - (dto.name.pascal.s)

  models:
    paths: [src, types, models]
    select: schemas.models.each

    imports:
      enums: enums

    symbols:
      - (model.name.pascal.s)

  typesIndex:
    paths: [src, types]
    exports: [enums, dtos, models]

  services:
    paths: [src, services]
    select: resources.each

    imports:
      types: typesIndex

    symbols:
      - (resource.name.pascal.s)Service

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

executables:
  packageManager: pnpm

commands:
  after:
    installDependencies:
      executable: packageManager
      arguments:
        - add
        - axios@^1.0.0

    format:
      executable: packageManager
      arguments:
        - exec
        - prettier
        - --write
        - src
      optional: true
```

## Pack filesystem

```text
typescript-sdk/
├── CodepotgPack.yaml
└── templates/
    ├── {enums}/
    │   └── (enum.name.kebab.s).ts.jinja
    │
    ├── {dtos}/
    │   └── (dto.name.kebab.s).dto.ts.jinja
    │
    ├── {models}/
    │   └── (model.name.kebab.s).model.ts.jinja
    │
    ├── {typesIndex}/
    │   └── index.ts.jinja
    │
    ├── {services}/
    │   └── (resource.name.kebab.s).service.ts.jinja
    │
    ├── {servicesIndex}/
    │   └── index.ts.jinja
    │
    ├── {client}/
    │   └── (option.clientName).ts.jinja
    │
    ├── {rootIndex}/
    │   └── index.ts.jinja
    │
    ├── package.json.jinja
    └── tsconfig.json
```

## Example generated output

```text
packages/typescript-sdk/
├── package.json
├── tsconfig.json
└── src/
    ├── index.ts
    ├── DefyTicketsClient.ts
    ├── services/
    │   ├── index.ts
    │   ├── orders.service.ts
    │   └── customers.service.ts
    └── types/
        ├── index.ts
        ├── enums/
        │   └── order-status.ts
        ├── dtos/
        │   └── create-order.dto.ts
        └── models/
            └── order.model.ts
```

The service selection imports from the types barrel:

```yaml
imports:
  types: typesIndex
```

This allows the resolver to generate one barrel import when suitable:

```ts
import type {
  CreateOrderDto,
  Order,
  OrderStatus,
} from "../types";
```

Instead of several direct imports.

The pack template still decides where the generated import block appears.

---

# 4. Flutter SDK pack

## `packs/flutter-sdk/CodepotgPack.yaml`

```yaml
apiVersion: codepotg.dev/v2
id: alidantech/flutter-sdk
version: 1.0.0
description: Generates a Dart and Flutter API client.

requires:
  codepotg: ">=2.0 <3.0"

options:
  clientName:
    default: ApiClient

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

    symbols:
      - (model.name.pascal.s)

  modelsIndex:
    paths: [lib, src, models]
    exports: [enums, models]

  services:
    paths: [lib, src, services]
    select: resources.each

    imports:
      models: modelsIndex

    symbols:
      - (resource.name.pascal.s)Service

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

executables:
  flutter: flutter

commands:
  after:
    installRuntimeDependencies:
      executable: flutter
      arguments:
        - pub
        - add
        - dio:^5.0.0
        - json_annotation:^4.0.0

    installDevelopmentDependencies:
      executable: flutter
      arguments:
        - pub
        - add
        - --dev
        - build_runner:^2.0.0
        - json_serializable:^6.0.0

    generateSerialization:
      executable: flutter
      arguments:
        - pub
        - run
        - build_runner
        - build
        - --delete-conflicting-outputs

    format:
      executable: dart
      arguments: [format, lib]
      optional: true
```

## Pack filesystem

```text
flutter-sdk/
├── CodepotgPack.yaml
└── templates/
    ├── {enums}/
    │   └── (enum.name.snake.s).dart.jinja
    │
    ├── {models}/
    │   └── (model.name.snake.s).dart.jinja
    │
    ├── {modelsIndex}/
    │   └── models.dart.jinja
    │
    ├── {services}/
    │   └── (resource.name.snake.s)_service.dart.jinja
    │
    ├── {servicesIndex}/
    │   └── services.dart.jinja
    │
    ├── {client}/
    │   └── (option.clientName.snake.o).dart.jinja
    │
    ├── {packageIndex}/
    │   └── defytickets_sdk.dart.jinja
    │
    ├── pubspec.yaml.jinja
    └── analysis_options.yaml
```

## Example generated output

```text
apps/mobile/
├── pubspec.yaml
├── analysis_options.yaml
└── lib/
    ├── defytickets_sdk.dart
    └── src/
        ├── api_client.dart
        ├── models/
        │   ├── models.dart
        │   ├── order.dart
        │   └── order_status.dart
        └── services/
            ├── services.dart
            ├── orders_service.dart
            └── customers_service.dart
```

---

# Common rules demonstrated

## Selection folders

```text
{repositories}
{models}
{services}
{rootIndex}
```

A folder enclosed in `{}` must match a registered selection key.

```yaml
selections:
  repositories:
    paths: [src, repositories]
```

The folder itself does not appear in the generated output.

---

## Name expressions

```text
(entity.name.kebab.s)
(model.name.snake.s)
(resource.name.pascal.s)
```

Single parentheses resolve expressions.

```text
((admin))
```

Emits a literal folder or filename containing:

```text
(admin)
```

---

## Literal files

These require no selection registration:

```text
templates/package.json.jinja
templates/pubspec.yaml.jinja
templates/README.md
templates/assets/logo.png
```

They emit relative to the pack emission root:

```text
package.json
pubspec.yaml
README.md
assets/logo.png
```

Rules:

* `.jinja` files are rendered and lose the `.jinja` extension.
* Other text and binary files are copied unchanged.
* `_partials` files are available to templates and are not emitted.
* Pack ignore rules and explicit exclusions are respected.

---

## `{root}` built-in

A pack may organize root-emitted templates under:

```text
templates/{root}/
```

For example:

```text
templates/{root}/package.json.jinja
templates/{root}/README.md.jinja
```

Both emit directly at the pack emission root.

`root` does not need to be declared under `selections`.

---

## Imports

```yaml
imports:
  localName: selectionKey
```

Example:

```yaml
imports:
  entities: entities
  types: typesIndex
```

This means:

* the dependency is mandatory and explicit;
* the referenced selection must exist;
* the import resolver may satisfy dependencies only through that selection;
* only required symbols are imported;
* conflicts and ambiguous symbols are errors;
* the language adapter writes the final target-language import syntax.

---

## Exports

```yaml
exports: [enums, dtos, models]
```

This creates an aggregate emission such as a barrel.

It:

* waits for the listed selections to be planned;
* receives their emitted paths and symbols;
* preserves the declared selection order;
* allows the template to choose wildcard or explicit exports;
* can export other barrel selections.

No separate `barrel`, `aggregate`, or `outputs.*` syntax is needed.

---

## Commands

Commands contain exact arguments authored by the pack:

```yaml
installDependencies:
  executable: packageManager
  arguments:
    - add
    - typeorm@^0.3.0
```

CodepotG does not convert dependency formats or understand package-manager installation rules.

The pack provides:

* executable default;
* exact arguments;
* lifecycle position.

The project may provide another executable:

```yaml
executables:
  packageManager: pnpm
```

Or a full path:

```yaml
executables:
  packageManager: ./tools/pnpm
```

Changing to a tool with incompatible arguments requires overriding the corresponding command, not automatic argument conversion.
