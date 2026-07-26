# Flutter SDK tokenized path-authoring tasks

## PACK-FLUTTER-PATH-001 — Package and integration paths

**Dependencies:** PATH-001..PATH-010, Dart adapter, Flutter/Dart ecosystem contracts

- [ ] Author generated API models under tokenized Dart source paths.
- [ ] Author clients/services/providers/adapters with explicit case/plurality name tokens.
- [ ] Author package/export files and static assets through structural or selection-bearing path recipes.
- [ ] Support both owned standalone-package roots and contributed existing-app roots.

## PACK-FLUTTER-PATH-002 — Framework boundaries

- [ ] Keep Dart filename validation in the Dart adapter.
- [ ] Keep Flutter project/unit detection in the ecosystem/framework integration layer.
- [ ] Keep output folder decisions in the pack source tree and `paths` recipes.
- [ ] Do not derive destinations from UI/state-management framework internals unless exposed as typed pack options or bindings.

## PACK-FLUTTER-PATH-003 — Conformance

- [ ] Test modular and monolithic profiles.
- [ ] Test package name, resource name, model name, nested folder, static asset, export barrel, and generated documentation paths.
- [ ] Test existing-app integration and standalone-package generation.
- [ ] Prove no ordinary descriptor needs explicit output configuration.
- [ ] Prove no semantic fixture exposes `fileName`, `filePath`, or `directory`.

**Acceptance:** Flutter fixtures use the shared path-expression subsystem and contain no private pack filename algorithm.
