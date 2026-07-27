# Dart SDK pack design reference

## Purpose

This pack generates one coherent standalone modular Dart SDK package from the closed CodepotG kernel.

It consumes group-rooted schemas and operations and authors every Dart/YAML/Markdown character through templates, macros, partials, and static files.

## Product boundary

The pack owns:

- object/enum schema type files;
- group-scoped client files iterating `group.operations`;
- operation input/output/failure handling;
- authored Dart export files;
- errors, runtime abstractions, package files, docs, examples, and static analysis configuration;
- documented bindings and exact optional commands.

It does not implement hidden standalone/contribution/modular/monolithic profiles. Existing-project contribution, Flutter integration, or a materially different single-file SDK should be separate packs.

## Selection design

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

  packageIndex:
    paths: [lib]
    exports: [typesIndex, clientsIndex]
```

The pack does not use neutral models, resources, services, requests, responses, or entities as selectors/context roots. A template may emit a class or service name as Dart output vocabulary.

## File examples

```text
templates/
├── {enums}/(schema.name.snake.s).dart.jinja
├── {schemaTypes}/(schema.name.snake.s).dart.jinja
├── {typesIndex}/types.dart.jinja
├── {groupClients}/(group.name.snake.s)_client.dart.jinja
├── {clientsIndex}/clients.dart.jinja
├── {packageIndex}/api_sdk.dart.jinja
├── pubspec.yaml.jinja
├── README.md.jinja
├── analysis_options.yaml
├── .gitignore.jinja
└── _partials/
    ├── license.txt.jinja
    ├── render-type.dart.jinja
    └── render-imports.dart.jinja
```

Export/import directives are authored templates/macros. Static files copy unchanged.

## Template syntax ownership

Templates author:

- classes, enums, typedefs, fields, constructors, methods, and functions;
- optional/nullable/generic/collection/function/Future syntax;
- imports, exports, prefixes, show/hide, and package/relative URI directives;
- literals, comments, annotations, serialization, and formatting;
- HTTP client calls and error/result handling.

The Dart target adapter validates filenames/candidate identifiers and supplies URI/path facts only.

## Project configuration example

```yaml
packs:
  dartSdk:
    source:
      git: https://github.com/alidantech-org/codepotg-packs.git
      ref: dart-sdk/v2.0.0
      path: packs/dart-sdk
    input: backendApi
    output: packages/api_sdk
    options:
      packageName: defytickets_api
```

The project does not list templates, global language, or a profile.

## Options, bindings, and commands

Pack options may configure authored SDK conventions such as package/client name, serialization, date/binary, transport, and error strategy.

Bindings may provide transport, authentication, base URL, logging, error mapping, serialization helpers, or package/project modules. Generated dependencies remain explicit under selection `imports`/`exports`.

`pub get`, format, analyze, test, or build-runner actions are exact optional commands and remain subject to project/host approval.

## Boundaries

- The pack consumes only the documented closed kernel and fixed selectors.
- It cannot add semantic objects/facets/selectors/context values.
- It authors all Dart syntax; the Dart adapter does not render it.
- Pubspec/project contribution logic outside the owned package belongs to a separate ecosystem/product contract.
- It does not parse OpenAPI, old pack files, profiles, `filePatterns`, or `paths.yaml`.

See `../tasks/00-package-plan.md`.
