# codepotg-language-dart

Installable Dart target-language adapter for CodepotG v2.

The adapter is resolved per `.dart` template and owns Dart syntax and typed language rules. Flutter remains a framework/template-pack concern and must not be embedded in this language adapter.

## Planned entry point

```toml
[project.entry-points."codepotg.language_adapters"]
dart = "codepotg_language_dart.plugin:create_plugin"
```

## Responsibilities

- Dart identifiers, reserved words, null safety, types, literals, comments, imports, exports, and library paths;
- relative and `package:` import planning, project-path conversion, barrel-style export files, and collision handling;
- typed rules, patches, merge semantics, override restrictions, and conformance tests;
- deterministic behavior usable by SDK, server, command-line, and Flutter packs.

See [`docs/tasks/00-package-plan.md`](docs/tasks/00-package-plan.md).
