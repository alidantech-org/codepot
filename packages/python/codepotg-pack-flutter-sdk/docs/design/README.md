# Flutter application-integration pack design reference

## Purpose

This pack applies Flutter conventions through authored Dart and Flutter templates. Flutter is not a language alias, and the Dart target adapter does not render Dart syntax.

The pack represents one generated integration layer for a host Flutter application. It consumes known groups, schemas, operations, and views from the closed CodepotG kernel.

## Semantic inputs

```text
contract.groups
group.schemas
group.operations
group.views
view.parts
view.triggers
view.flows
operation.inputs
operation.outputs
operation.failures
operation.effects
operation.facets.http
operation.facets.access
```

The pack does not invent views from HTTP operations. View files emit only when the source contains known `group.views` declarations.

## Product boundary

The pack may generate:

- Dart schema and enum types;
- group-scoped API clients;
- Flutter view files from declared views;
- trigger-to-operation wiring from declared relationships;
- error, transport, configuration, and state abstractions;
- authored export files;
- documentation and static assets;
- known host-project dependency and asset contributions;
- exact optional format, analyze, test, and build-runner commands.

It does not implement hidden standalone, existing-app, minimal, provider, or monolithic profiles. A materially different state-management, package, or interaction architecture should be a separate pack.

## Selection design

```yaml
selections:
  enums:
    paths: [lib, generated, types, enums]
    select: groups.schemas.enums.each
    symbols:
      - (schema.name.pascal.s)

  schemaTypes:
    paths: [lib, generated, types, schemas]
    select: groups.schemas.objects.each
    imports:
      enums: enums
    symbols:
      - (schema.name.pascal.s)

  typesIndex:
    paths: [lib, generated, types]
    exports: [enums, schemaTypes]

  groupClients:
    paths: [lib, generated, clients]
    select: groups.each
    imports:
      types: typesIndex
    symbols:
      - (group.name.pascal.s)Client

  views:
    paths: [lib, generated, views]
    select: groups.views.each
    imports:
      types: typesIndex
      clients: groupClients
    symbols:
      - (view.name.pascal.s)View

  generatedIndex:
    paths: [lib, generated]
    exports: [typesIndex, groupClients, views]
```

`View` is authored Flutter output vocabulary. The neutral selected object is `view`. The pack never selects neutral model, resource, service, frontend, UI, screen, page, component, widget, or entity roots.

## File examples

```text
templates/
├── {enums}/(schema.name.snake.s).dart.jinja
├── {schemaTypes}/(schema.name.snake.s).dart.jinja
├── {typesIndex}/types.dart.jinja
├── {groupClients}/(group.name.snake.s)_client.dart.jinja
├── {views}/(view.name.snake.s)_view.dart.jinja
├── {generatedIndex}/generated.dart.jinja
├── README.generated.md.jinja
├── analysis_options.generated.yaml
├── assets/example.json
└── _partials/
    ├── render-type.dart.jinja
    ├── render-imports.dart.jinja
    ├── render-view-trigger.dart.jinja
    └── license.txt.jinja
```

Selection-scoped templates fan out from known semantic contexts. Static assets copy unchanged.

## Template syntax ownership

The pack authors all Dart and Flutter text, including types, nullability, imports, exports, annotations, serialization, widgets, layouts, routes, forms, state integration, operation calls, access presentation, comments, literals, and formatting.

The Dart target adapter validates output and candidate names and supplies URI and path facts only.

## Project configuration example

```yaml
packs:
  mobileIntegration:
    source:
      git: https://github.com/alidantech-org/codepotg-packs.git
      ref: flutter-integration/v2.0.0
      path: packs/flutter-integration
    input: backendApi
    output: apps/mobile
    bindings:
      transport:
        from: riderescue_core/network/app_http_client.dart
        symbol: AppHttpClient
```

No `use`, profile, global language, output-root object, or internal template list is required.

## Host integration

Host Flutter and Dart dependencies, assets, and project changes use known ecosystem contribution contracts where implemented. Exact commands remain authored commands subject to approval.

## Boundaries

- The pack consumes only known closed-kernel concepts and root-first selectors.
- It cannot add frontend, UI, screen, widget, facet, selector, or arbitrary context concepts.
- Every generated Dart and Flutter character is authored in pack files.
- Materially different architecture choices become separate packs.
- Dart target detection and path facts remain in the Dart adapter; it does not render syntax.
- The pack does not parse OpenAPI, old pack formats, profiles, or `filePatterns`.

See `../tasks/00-package-plan.md`.
