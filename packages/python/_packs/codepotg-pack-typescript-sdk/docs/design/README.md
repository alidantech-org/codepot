# TypeScript SDK pack design reference

## Purpose

This pack generates one coherent modular, framework-neutral TypeScript SDK product from the closed CodepotG kernel.

It consumes:

```text
contract.groups
group.schemas
group.operations
operation.inputs
operation.outputs
operation.failures
operation.effects
operation.facets.http
```

Other known facts such as access/events may be used for documentation or optional authored behavior only when explicitly represented by the kernel input.

## Product boundary

The pack generates a modular SDK package with:

- schema and enum type files;
- group-scoped client files iterating group operations;
- error/runtime abstractions;
- authored barrels;
- package/configuration/documentation templates;
- static files;
- documented bindings and exact optional commands.

It does not implement hidden `profiles`, file-ID activation, or root `filePatterns`. A materially different monolithic SDK, framework client, or existing-project contribution product should be a separate pack with its own identity and templates.

## Selection design

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

The pack does not use neutral `model`, `resource`, `service`, request, response, or entity contexts. Those may be names emitted by authored TypeScript templates where appropriate.

## File examples

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
├── tsconfig.json
├── README.md.jinja
├── .gitignore.jinja
└── _partials/
    ├── license.txt.jinja
    ├── render-type.ts.jinja
    └── render-imports.ts.jinja
```

Barrels and imports are authored templates/macros. Static files copy unchanged. Ordinary files are discovered from the filesystem.

## Template syntax ownership

The TypeScript target adapter supplies validated target/module-path facts. Templates author:

- interfaces, type aliases, classes, enums, functions, and methods;
- optional/nullable/union/array/map syntax;
- imports and exports;
- literals, comments, docs, quotes, semicolons, and formatting;
- HTTP calls and response/error handling;
- annotations, validators, or framework syntax when a different pack explicitly chooses them.

Example:

```jinja
{% for module in imports.types.modules %}
import type { {{ module.symbols | join(", ") }} } from "{{ module.specifier }}";
{% endfor %}
```

No target adapter injects that line.

## Options and bindings

Pack options may select authored SDK conventions such as client name, transport shape, date/binary representation, error strategy, and examples where templates can express them without changing the emission registry.

Bindings may provide project/package modules, transport abstractions, authentication, configuration, logging, or error helpers. Generated selection dependencies remain separate and explicit under `imports`/`exports`.

Options and bindings cannot add semantic kernel properties or arbitrary template context.

## Project configuration example

```yaml
packs:
  sdk:
    source:
      git: https://github.com/alidantech-org/codepotg-packs.git
      ref: typescript-sdk/v2.4.1
      path: packs/typescript-sdk
    input: backendApi
    output: packages/api-sdk
    options:
      clientName: ApiClient
```

The project user does not list internal templates or select a global language/profile.

## Boundaries

The pack:

- consumes only documented closed-kernel contexts and fixed selectors;
- cannot add facets/selectors/expression roots/context values;
- authors all generated TypeScript syntax;
- does not parse OpenAPI or old pack files;
- does not write files or run commands from templates;
- does not rely on old `paths.yaml`, profiles, `filePatterns`, or hidden barrels.

See `../tasks/00-package-plan.md` for the implementation ledger.
