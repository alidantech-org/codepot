# Dart target adapter design reference

## Role

This package is resolved for templates whose target suffix is `.dart`. It detects and validates Dart targets and calculates target-aware URI/path facts from already planned artifacts.

It never selects templates, extends the semantic kernel, assumes Flutter, or authors Dart source text.

## Planned plugin entry point

```toml
[project.entry-points."dryv.language_adapters"]
dart = "dryv_language_dart.plugin:create_plugin"
```

## Typed target options

Options are limited to target detection, filename/identifier validation, and URI/path facts. A possible shape is:

```yaml
targets:
  dart:
    modules:
      strategy: relative
      packageName: null
    validation:
      reservedWordPolicy: diagnostic
```

Every option is typed, immutable, validated, documented, and introspectable. Raw dictionaries and generic recursive merges are prohibited.

The adapter must not define options for generated type/null-safety mapping, literals, comments, imports/exports syntax, annotations, serialization, formatting, or Flutter behavior. Packs implement those through templates/macros and pack options.

## URI/path facts

Given planned provider and consumer artifacts, the adapter may calculate and validate:

```text
relative URI segments
normalized relative URI
package URI from an explicit package-name/project-path binding
explicit package/module identity
export/barrel provider destination
path containment and escaping diagnostics
```

Example descriptor supplied to a template:

```text
module.symbols = [User]
module.uri = package:defytickets_sdk/src/types/user.dart
module.is_package = true
```

The template authors the statement:

```jinja
import '{{ module.uri }}' show {{ module.symbols | join(", ") }};
```

The adapter does not return the rendered line and does not choose quote style, prefixes, deferred imports, show/hide combinators, ordering, grouping, or export statement form.

## Identifier and filename validation

Core supplies semantic naming projections using:

```text
x.name.{casing}.{number}
```

Templates select the projection they need. The adapter may validate an authored candidate as a Dart type, variable, field, parameter, library prefix, or file stem and return diagnostics/facts. It does not automatically rename semantic objects or expose APIs such as `dart.className`.

## Internal implementation shape

```text
DartTargetAdapter
├── TargetDescriptor
├── FileNameValidator
├── IdentifierValidator
├── ReservedWordCatalog
├── UriResolver
├── PackagePathValidator
└── CapabilityDescriptor
```

No type renderer, literal/comment renderer, import planner/renderer, export renderer, annotation renderer, or formatter belongs in this package.

## Boundaries

This package does not own:

- semantic objects, facets, selectors, or expression roots;
- generated Dart type/null-safety/literal/comment/import/export/annotation syntax;
- Flutter widgets, state management, navigation, or application layout;
- `pubspec.yaml` updates or `dart pub get`;
- semantic source parsing;
- template rendering or selection;
- destination planning/writing;
- commands;
- old generator behavior.

See `../tasks/00-package-plan.md` and the core target adapter contract.
