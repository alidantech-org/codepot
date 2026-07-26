# codepotg-language-dart

Installable Dart target detection, validation, and URI/path adapter for CodepotG v2.

The adapter is resolved per `.dart` template. It does **not** own Dart code generation. Template packs, macros, partials, and static files author every Dart character, including types, literals, comments, imports, exports, annotations, serialization, and Flutter code.

Flutter remains framework/template-pack policy and must not be embedded in this target adapter.

## Planned entry point

```toml
[project.entry-points."codepotg.language_adapters"]
dart = "codepotg_language_dart.plugin:create_plugin"
```

## Responsibilities

- `.dart` target detection and output filename validation;
- Dart reserved-name and declared candidate-identifier validation;
- relative URI, `package:` URI, project-path, export/barrel destination, and path-containment facts;
- deterministic target/path capability descriptors and typed validation options;
- diagnostics, introspection, compatibility, and conformance behavior.

## Prohibited responsibilities

- semantic-kernel/facet/selector extension;
- Dart type, literal, comment, import, export, annotation, or formatting rendering;
- Flutter widgets/state/layout policy;
- template selection, output planning, pubspec changes, filesystem writes, commands, or source parsing.

See [`docs/design/README.md`](docs/design/README.md) and [`docs/tasks/00-package-plan.md`](docs/tasks/00-package-plan.md).
