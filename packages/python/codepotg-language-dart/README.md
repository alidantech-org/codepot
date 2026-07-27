# codepotg-language-dart

Pure-Python Dart target validation and URI facts for CodepotG v2.

## Baseline

- Language baseline: Dart 3.12.2 identifier, keyword, privacy, and URI subset.
- Behavior version: `1`.
- Date verified: 2026-07-27.
- Supported output suffix: `.dart`.
- Identifier subset: ASCII by default; a specification-oriented Unicode-category policy is available.
- URI forms: canonical relative URIs with `./` for same-folder paths, explicit `dart:` URIs, explicit `package:` URIs, and package URIs built only from explicit package/library-root facts.
- Private names: a leading underscore is preserved and reported as an informational fact by default.
- Unsupported: Flutter assumptions, hidden barrel/index rewriting, symbol combinators, import/export rendering, project configuration decoding, and diagnostics on `ModulePathFacts`.

Templates own every emitted Dart character.
