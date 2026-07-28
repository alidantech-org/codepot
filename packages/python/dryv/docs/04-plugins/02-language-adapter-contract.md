# Language and target adapter contract

## Responsibility

A target adapter describes and validates one target syntax for already planned template artifacts. It is resolved independently from the detected target suffix.

A project and pack may use several targets in one run.

A target adapter is not a code renderer. Templates, macros, partials, and static files own every emitted character.

## Installable package

Examples:

```text
dryv-language-typescript
dryv-language-dart
acme-dryv-language-csharp
```

Each package registers a factory through `dryv.language_adapters`.

## Target descriptors

A plugin declares one or more descriptors containing:

```text
id
aliases
file extensions
syntax category
filename and reserved-name validation behavior
module/path capabilities
supported validation capabilities
behavior version
```

Extension resolution uses longest-known matching. Removing an engine suffix never removes the intended target suffix.

## Allowed services

A target adapter may provide:

- extension registration and inference;
- filename/stem validation;
- reserved filename and identifier diagnostics;
- validation facts for explicitly supplied candidate identifiers;
- destination-relative module/path normalization;
- module specifier validation;
- index and extension conventions needed for path facts;
- package/module/namespace validation for project bindings;
- deterministic capability reporting.

It returns typed immutable facts and diagnostics, never target-source snippets.

## Prohibited syntax services

A target adapter must not render or inject:

- primitive or composite type syntax;
- optional or nullable syntax;
- generics, unions, intersections, functions, records, arrays, or maps;
- enum declarations;
- emitted literals or escaping;
- comments or documentation comments;
- imports or exports;
- decorators, annotations, validators, modifiers, or framework calls;
- class, interface, type, struct, record, trait, repository, controller, widget, or entity syntax;
- formatting, quotes, indentation, semicolons, or textual order.

Those belong to packs and templates.

## Naming boundary

Dryv owns semantic name projections:

```text
x.name.{casing}.{number}
```

Target plugins do not create alternate semantic naming APIs. Templates select documented projections and may use pack-authored macros for output conventions.

## Module/path facts

Dryv plans provider and consumer artifacts. A target adapter may calculate or validate target-aware facts from their final destinations and explicit project bindings.

A module descriptor may expose:

```text
provider artifact identity
consumer artifact identity
relative path segments
normalized module specifier
extension/index requirements
package/module identity
symbols
validation diagnostics
```

The template authors the final statement:

```jinja
{% for module in imports.schemaType.modules %}
import type { {{ module.symbols | join(", ") }} } from "{{ module.specifier }}";
{% endfor %}
```

The plugin never returns that rendered line.

## Target options

Target configuration is limited to detection, path calculation, validation, and capability reporting.

```yaml
targets:
  typescript:
    files: {}
    modules: {}
    validation: {}
```

Generated type mapping, literals, comment style, imports, exports, decorators, framework conventions, and formatting belong to pack options and templates.

Every supported target option is typed, documented, introspectable, immutable, and behavior-versioned.

## Context safety

The adapter receives the minimum immutable planned artifacts, paths, options, and cancellation required for its operation. It cannot mutate semantic IR, selections, artifacts, pack files, or prepared template contexts.

## Prohibited responsibilities

A target adapter must not:

- load or interpret semantic contracts;
- extend the kernel or register facets/selectors;
- select semantic records or templates;
- discover or resolve packs;
- render templates;
- render target syntax;
- write output files;
- execute commands;
- own cache persistence;
- inspect CLI arguments;
- encode framework architecture;
- assume one language implies one framework or ecosystem.

## Conformance tests

Every target package tests:

- deterministic descriptor and suffix inference;
- longest-known extension matching;
- filename and reserved-name validation;
- candidate identifier validation where supported;
- relative and package module/path facts;
- index and extension policies;
- typed option validation and introspection;
- no emitted syntax or pre-rendered snippets;
- no semantic-kernel extension;
- immutable inputs and session isolation;
- plugin descriptor compatibility;
- wheel entry-point discovery.

Language packages add focused tests only for capabilities they actually publish.
