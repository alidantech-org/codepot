# Dart SDK selection-folder authoring tasks

## PACK-DART-PATH-001 — Author the package template tree

**Dependencies:** PATH-001..PATH-010, Dart target descriptor, Dart ecosystem contract

- [ ] Keep `pubspec.yaml.jinja`, `analysis_options.yaml`, documentation, and static files literal and unregistered.
- [ ] Place model templates under `{models}/(model.name.snake.s).dart.jinja`.
- [ ] Place services/clients under registered selection folders using explicit snake/path name expressions.
- [ ] Author export libraries as normal templates whose selections declare `exports`.
- [ ] Use `{root}` only when physical grouping should not add an output folder.

## PACK-DART-PATH-002 — Declare dependencies and outputs

- [ ] Use compact `paths: [lib, ...]` arrays relative to the pack-instance output root.
- [ ] Use fixed selectors such as `schemas.models.each`, `schemas.enums.each`, and `resources.each`.
- [ ] Declare generated dependencies with `imports` and generated libraries/barrels with `exports`.
- [ ] Declare emitted Dart symbols explicitly.
- [ ] Keep Dart filename/module validation in the Dart adapter.
- [ ] Keep `package:` versus relative import calculation separate from destination composition.

## PACK-DART-PATH-003 — Conformance

- [ ] Test singular/plural names, acronyms, nested resources, exports, static files, partials, and generated `.gitignore`.
- [ ] Test standalone package and existing-project output roots.
- [ ] Test direct versus barrel imports and least-required symbols.
- [ ] Prove no root `paths`, `files`, `filePatterns`, or ordinary explicit output fields are required.
- [ ] Prove no semantic fixture exposes `fileName`, `filePath`, or `directory`.

**Acceptance:** Dart fixtures resolve destinations from the filesystem, registered selections, fixed selectors, typed names, and the project output root.
