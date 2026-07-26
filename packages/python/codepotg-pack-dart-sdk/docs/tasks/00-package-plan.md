# Dart SDK pack tasks

## Package and manifest

- [ ] Add isolated package metadata, pack-provider entry point, package-data rules, and compatibility bounds.
- [ ] Add `CodepotgPack.yaml` covering content, files, selections, bindings, Dart rules, Pub dependencies, setup, commands, lifecycle, and outputs.
- [ ] Model both standalone-subtree ownership with an owned `pubspec.yaml` and contributed-file integration into an existing Dart package.

## Pack content

- [ ] Migrate representative enums, models, serialization, requests, responses, operations, API clients, errors, exports, documentation, and tests.
- [ ] Use authored Dart export templates instead of hidden barrel generation.
- [ ] Include static `.gitignore`, analysis options, examples, license, and package files where appropriate.
- [ ] Support per-model, grouped, and complete single-file generation profiles.
- [ ] Support template and static-file fan-out through folder patterns.

## Bindings, dependencies, and setup

- [ ] Declare and document public package, project-path, barrel/export, text, and artifact bindings.
- [ ] Support relative and `package:` imports using project package names and target locations.
- [ ] Declare typed hosted, Git, path, runtime, and development dependencies.
- [ ] Add typed actions for `dart pub get`, formatting, analysis, tests, and build runners under command policy.
- [ ] Provide configure discovery, questions, examples, and manual integration guidance.

## Validation and migration

- [ ] Pass pack contract suites for manifests, templates, static files, imports, bindings, and actions.
- [ ] Generate small fixtures plus a realistic standalone Dart API package with its own `pubspec.yaml`.
- [ ] Compare against existing Dart pack outputs and classify intentional differences.
- [ ] Prove local, Git, private GitHub, cache, and lock-file resolution.
- [ ] Version and publish independently.
