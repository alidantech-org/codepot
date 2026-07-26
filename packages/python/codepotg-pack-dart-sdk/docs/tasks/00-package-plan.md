# Dart SDK pack implementation plan

This package authors a new v2 Dart SDK pack. It does not parse old pack files or import old generator code.

## PACK-DART-001 — Package and provider foundation

**Status:** planned

- [ ] Add isolated package metadata, package-data rules, README, and tests.
- [ ] Include `CodepotgPack.yaml`, templates, static/binary assets, partials, docs, and examples in wheel/sdist.
- [ ] Declare core, pack-schema, IR, Dart adapter, Jinja engine, and Dart ecosystem compatibility.

## PACK-DART-002 — Manifest traits and profiles

- [ ] Define standalone subtree/package profile with owned `pubspec.yaml`.
- [ ] Define existing Dart package contribution profile.
- [ ] Define modular, grouped, minimal, and complete single-file profiles where useful.
- [ ] Define content roots, ignore rules, write policy, compatibility, and override policy.

## PACK-DART-003 — Typed pack options

- [ ] Define package name/version/description options for owned package output.
- [ ] Define modular/monolithic and feature toggles.
- [ ] Define serialization, client style, date/binary/error strategy as pack policy connected to Dart adapter capabilities.
- [ ] Define examples/tests/docs options.
- [ ] Add validation, defaults, docs, examples, and configure prompts.

## PACK-DART-004 — Selections

- [ ] Define deterministic selections for enums, models, requests, responses, operations, resources, errors, and aggregate project context.
- [ ] Define grouped resources/client services.
- [ ] Define artifact-derived selections for authored export templates.
- [ ] Define complete aggregate context for one-file generation.

## PACK-DART-005 — Template and static inventory

Author new files for:

- [ ] enums/models and JSON serialization metadata;
- [ ] request/response DTOs;
- [ ] operation/client/service files;
- [ ] errors and transport abstractions;
- [ ] shared utilities/configuration;
- [ ] authored `exports.dart.jinja` or `index.dart.jinja` templates;
- [ ] docs/examples/tests;
- [ ] neutral partials;
- [ ] static `.gitignore`, `analysis_options.yaml`, license, examples, fixtures, assets;
- [ ] owned `pubspec.yaml.jinja` and package files for standalone profile.

No hidden export/barrel subsystem is allowed.

## PACK-DART-006 — Patterns and target inference

- [ ] Use folder patterns for per-model/resource output and static fan-out where useful.
- [ ] Infer Dart, YAML, Markdown, and other target syntax from filenames.
- [ ] Define exact outputs and profiles without duplicate descriptors.
- [ ] Prove static files copy without rendering.

## PACK-DART-007 — Binding catalog

Declare and document bindings for:

- [ ] HTTP transport/client;
- [ ] authentication/token provider;
- [ ] base URL/config provider;
- [ ] error mapper;
- [ ] logger;
- [ ] package name/import root;
- [ ] serialization helpers or project abstractions;
- [ ] artifact references to other packs.

For every binding:

- [ ] list exact template consumers;
- [ ] support package URI, project path, relative URI, export/barrel group, explicit URI, text/value, and raw escape where meaningful;
- [ ] provide discovery hints and missing policy;
- [ ] allow one project export/barrel to satisfy multiple symbols.

## PACK-DART-008 — Dart and Jinja rules

- [ ] Define pack Dart defaults using only published adapter rules.
- [ ] Define import strategy defaults for standalone package and contribution profiles.
- [ ] Define safe Jinja rules.
- [ ] Define permitted project overrides and protect pack invariants.

## PACK-DART-009 — Dependencies and manifests

- [ ] Declare typed hosted, Git, path, runtime, and development dependencies.
- [ ] For standalone profile, own complete `pubspec.yaml` and package metadata.
- [ ] For contribution profile, plan typed pubspec changes rather than replacing user files.
- [ ] Support Dart/Flutter workspace registration where declared.
- [ ] Keep dependency declaration separate from `dart pub get` execution.

## PACK-DART-010 — Setup, actions, and documentation

- [ ] Define configure questions for package identity, profile, imports, bindings, and options.
- [ ] Detect existing pubspec, package name, workspace, SDK, and candidate project abstractions.
- [ ] Define typed optional actions for dependency resolution, `dart format`, `dart analyze`, tests, and build runner.
- [ ] Declare action phases/capabilities and approval behavior.
- [ ] Add manual integration steps and setup docs.

## PACK-DART-011 — Small fixtures

- [ ] Generate one enum, model, request, response, operation, error, and authored export file.
- [ ] Test standalone package and contributed-file profiles.
- [ ] Test package URI and relative URI bindings.
- [ ] Test default export/barrel binding group.
- [ ] Test monolithic single-file output, static files, folder fan-out, ignores, missing binding policies, and strict readiness.

## PACK-DART-012 — Realistic standalone package

- [ ] Generate an inspectable API client package with its own `pubspec.yaml`, docs, examples, analysis config, and tests.
- [ ] Run format/analyze/tests when repository toolchain permits.
- [ ] Validate package import paths and owned-manifest output.

## PACK-DART-013 — Realistic existing-package integration

- [ ] Generate into a controlled existing Dart package.
- [ ] Plan pubspec contributions without replacing unrelated content.
- [ ] Test project-path and package URI resolution from actual output paths.
- [ ] Produce manual/readiness report for remaining host integration.

## PACK-DART-014 — Distribution and release

- [ ] Prove local, Git/GitHub, locked commit, and installed distribution pack resolution.
- [ ] Inspect representative old outputs only for requirements and record intentional differences.
- [ ] Do not add old pack/config runtime compatibility.
- [ ] Pass all pack/file/binding/rule/dependency/action/integration suites.
- [ ] Build wheel/sdist with all pack data and publish independently.

## Completion gate

- standalone and contributed profiles work through the v2 manifest only;
- package and relative imports are correct;
- authored exports and static files work;
- bindings, dependencies, setup, and actions are documented;
- realistic package validates;
- no old `paths.yaml` or generator implementation dependency exists.
