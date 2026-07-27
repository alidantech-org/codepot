# Flutter SDK selection-folder authoring tasks

## PACK-FLUTTER-PATH-001 — Package and integration template tree

**Dependencies:** PATH-001..PATH-010, Dart adapter, Flutter/Dart ecosystem contracts

- [ ] Place models, enums, services, and clients under registered selection folders.
- [ ] Use `(name.case.number)` expressions for generated Dart filenames.
- [ ] Author package/export libraries as normal templates whose selections declare `exports`.
- [ ] Keep `pubspec.yaml.jinja`, analysis options, assets, docs, and other literal files unregistered.
- [ ] Support both standalone package and existing-app output roots through project `output` plus pack-relative `lib` paths.

## PACK-FLUTTER-PATH-002 — Framework boundaries

- [ ] Keep Dart filename and import validation in the Dart adapter.
- [ ] Keep Flutter project/unit detection in the ecosystem layer.
- [ ] Keep output folder decisions in the pack filesystem and selection `paths` arrays.
- [ ] Declare generated dependencies through `imports` and symbols explicitly.
- [ ] Do not derive destinations from UI/state-management internals unless exposed as typed options or bindings.

## PACK-FLUTTER-PATH-003 — Conformance

- [ ] Load `codepotg-v2/docs/examples/packs/flutter-sdk.CodepotgPack.yaml` as the baseline fixture.
- [ ] Test package, resource, model, nested folder, static asset, barrel, and documentation paths.
- [ ] Test direct versus barrel imports, barrels exporting barrels, and least-required symbols.
- [ ] Test existing-app integration and standalone package generation.
- [ ] Prove no root `paths`, explicit `files`, or semantic filename conveniences exist.

**Acceptance:** Flutter fixtures use the shared selection-folder/path-expression subsystem and contain no private filename algorithm.
