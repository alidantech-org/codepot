# Dart adapter design reference

## Role

This package implements Dart target syntax for templates ending in `.dart.<engine>`. Flutter remains framework policy inside packs.

## Planned plugin entry point

```toml
[project.entry-points."codepotg.language_adapters"]
dart = "codepotg_language_dart.plugin:create_plugin"
```

## Pack rules example

```yaml
languages:
  dart:
    identifiers:
      reservedWordPolicy: suffix
      suffix: Value
    naming:
      types: pascalCase
      values: camelCase
      files: snakeCase
    imports:
      strategy: relative
      packageName: null
      ordering: [dart, package, relative]
      prefixes: automatic
      combinators: merge
      quoteStyle: single
    exports:
      ordering: stable
    types:
      nullSafety: enabled
      date: DateTime
      binary: Uint8List
      futureResponses: true
    comments:
      documentation: tripleSlash
```

Rules and overrides are typed and introspectable. A pack or project cannot supply arbitrary dictionaries.

## Import strategies

The adapter supports semantic import requests resolved as:

```dart
import '../models/user.dart';
import 'package:my_sdk/src/errors/api_exception.dart';
import 'package:shared/common.dart' show AppLogger, BaseRepository;
```

A project-path binding gives the adapter a real file path, allowing correct relative URI calculation. A package binding uses the configured package name. A barrel/export group may satisfy several logical symbols.

## Internal implementation shape

```text
DartLanguageAdapter
├── IdentifierPolicy
├── NamingPolicy
├── TypeRenderer
├── LiteralRenderer
├── CommentRenderer
├── UriResolver
├── ImportPlanner
└── ExportPlanner
```

## Boundaries

This package does not own:

- Flutter widgets or application layout;
- state management;
- `pubspec.yaml` updates or `dart pub get`;
- OpenAPI parsing;
- template rendering;
- file planning/writing;
- commands;
- old generator behavior.

See `../tasks/00-package-plan.md` and the core language adapter contract.
