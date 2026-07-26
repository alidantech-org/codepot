# Dart SDK tokenized path-authoring tasks

## PACK-DART-PATH-001 — Standalone package paths

**Dependencies:** PATH-001..PATH-010, Dart target descriptor, Dart ecosystem contract

- [ ] Author owned package files through structural recipes such as `{packageRoot}/pubspec.yaml.jinja` and `{packageRoot}/analysis_options.yaml`.
- [ ] Author model templates under `{models}/[model.name.snake.s].dart.jinja`.
- [ ] Author operations/clients under explicit snake/path name projections.
- [ ] Author export barrels as normal `.dart.jinja` templates.
- [ ] Copy static package files through tokenized paths without rendering.

## PACK-DART-PATH-002 — Existing-project integration

- [ ] Support a project output root plus package/unit path values without inventing directory fields on IR records.
- [ ] Test relative and `package:` imports independently from file destination composition.
- [ ] Test a package name binding used for imports but not silently used as an output folder.

## PACK-DART-PATH-003 — Conformance

- [ ] Test singular/plural model names, acronyms, nested resource paths, generated exports, and static fan-out.
- [ ] Test owned `pubspec.yaml`, contributed host files, modular output, and monolithic single-file output.
- [ ] Prove all normal outputs require no explicit manifest `output` field.
- [ ] Prove no semantic fixture exposes `fileName`, `filePath`, or `directory`.

**Acceptance:** standalone and hosted Dart fixtures resolve every destination from source paths, recipes, typed names, and project output roots.
