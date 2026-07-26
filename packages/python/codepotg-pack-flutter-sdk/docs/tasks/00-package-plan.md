# Flutter SDK/integration pack implementation plan

Flutter is framework policy built on the Dart language adapter and Dart ecosystem adapter. This package must not duplicate Dart syntax rendering.

## PACK-FLUTTER-001 — Package and provider foundation

**Status:** planned

- [ ] Add isolated package metadata, package-data rules, README, and tests.
- [ ] Include `CodepotgPack.yaml`, templates, static/binary assets, docs, partials, and examples.
- [ ] Declare compatibility with core, pack schema, IR, Dart adapter, Jinja engine, Dart ecosystem adapter, and supported Flutter/Dart SDK capabilities.

## PACK-FLUTTER-002 — Integration traits and profiles

- [ ] Define standalone generated Flutter/Dart package profile.
- [ ] Define existing Flutter application contribution profile.
- [ ] Define modular, minimal, and monolithic API layer profiles where useful.
- [ ] Define owned folder, contributed files, required dependencies/bindings, runnable-alone, and manifest mode traits accurately.
- [ ] Define content, ignore, write, compatibility, and override policy.

## PACK-FLUTTER-003 — Typed options

- [ ] Define package/app identity options.
- [ ] Define transport/provider/integration style options without forcing one state-management library by default.
- [ ] Define serialization, authentication, error, base URL, examples/tests/docs, and build-runner options.
- [ ] Put UI/state-management-specific behavior behind explicit profiles or options.
- [ ] Add defaults, validation, docs, examples, and configure prompts.

## PACK-FLUTTER-004 — Selections and artifacts

- [ ] Define model, enum, request, response, operation, service, resource, error, provider/adapter, and aggregate selections.
- [ ] Define artifact capabilities for generated API client, models, exports, and optional provider layer.
- [ ] Define authored export file selections from planned artifacts.

## PACK-FLUTTER-005 — Template/static inventory

Author new files for:

- [ ] Dart models/enums/serialization;
- [ ] requests/responses/operations/client/services;
- [ ] error mapping and transport interfaces;
- [ ] optional provider/adaptor integration files;
- [ ] authored export templates;
- [ ] docs/examples/tests;
- [ ] neutral partials;
- [ ] static `.gitignore`, `analysis_options.yaml`, `.env.example`, license, sample assets/configs;
- [ ] standalone package `pubspec.yaml.jinja` and package files where profile owns them.

No hidden export/barrel generation is allowed.

## PACK-FLUTTER-006 — File patterns and targets

- [ ] Use folder patterns for features/resources and static fan-out.
- [ ] Infer `.dart.jinja`, `.yaml.jinja`, `.md.jinja`, and other targets per file.
- [ ] Define profiles through stable file IDs.
- [ ] Validate no duplicate descriptor/output.

## PACK-FLUTTER-007 — Binding catalog

Declare/document exact template consumers for:

- [ ] HTTP transport or Dio-compatible abstraction;
- [ ] authentication token source;
- [ ] base URL/environment provider;
- [ ] error mapper;
- [ ] logging;
- [ ] project package name/import root;
- [ ] optional state/provider integration abstractions;
- [ ] generated artifact references.

Support package URI, project path, relative URI, export/barrel group, explicit URI, value/text, and raw escape where meaningful. Provide discovery hints and flexible missing policies.

## PACK-FLUTTER-008 — Framework requirements and rules

- [ ] Declare Flutter project/package capabilities and SDK constraints through ecosystem requirements.
- [ ] Define Dart rules only through fields published by the Dart adapter.
- [ ] Define safe Jinja rules.
- [ ] Define override policy and protect profile invariants.
- [ ] Keep framework folder/layout behavior inside pack templates and manifest, not Dart adapter.

## PACK-FLUTTER-009 — Dependencies and manifests

- [ ] Declare Flutter/Dart hosted, Git, path, runtime, and development dependencies by selected features.
- [ ] Plan existing `pubspec.yaml` contributions without replacing unrelated content.
- [ ] Own complete pubspec only for standalone package profile.
- [ ] Declare assets and workspace/package registration when required.
- [ ] Separate desired state from `flutter pub get`/build-runner actions.

## PACK-FLUTTER-010 — Configure and setup

- [ ] Detect Flutter project, pubspec, package name, workspace path, Dart/Flutter SDK, existing transport/auth/logger candidates, and chosen state-management dependencies.
- [ ] Ask typed questions only for missing public options/bindings.
- [ ] Define typed optional actions for pub get, format, analyze, tests, and build runner.
- [ ] Declare approvals/capabilities/phases.
- [ ] Add manual steps for wiring generated services/providers into the app.

## PACK-FLUTTER-011 — Small fixtures

- [ ] Generate one model, enum, request, response, operation, service, error, export, and optional provider integration.
- [ ] Test standalone and existing-app profiles.
- [ ] Test package/relative imports, default export barrel, static files, folder patterns, ignores, bindings, placeholders, and strict readiness.

## PACK-FLUTTER-012 — Realistic standalone package fixture

- [ ] Generate inspectable package with pubspec, analysis config, docs, examples, tests, and optional build-runner config.
- [ ] Run supported Flutter/Dart validation tools in controlled environments.

## PACK-FLUTTER-013 — Realistic app integration fixture

- [ ] Generate into a controlled existing Flutter app.
- [ ] Plan typed pubspec/assets contributions.
- [ ] Validate imports and manual setup report.
- [ ] Prove the app user does not need internal template knowledge.

## PACK-FLUTTER-014 — Distribution and release

- [ ] Prove local, Git/GitHub, lock, installed distribution, and digest-bound approval behavior.
- [ ] Inspect old outputs only for requirements; record intentional differences.
- [ ] Never implement old pack/config compatibility.
- [ ] Pass pack, framework capability, binding, dependency, action, security, and integration suites.
- [ ] Build wheel/sdist with all pack data and publish independently.

## Completion gate

- Flutter remains framework pack policy over Dart adapter semantics;
- standalone and existing-app profiles work through v2 contracts;
- dependencies/bindings/setup/actions are documented and secure;
- authored exports and static files work;
- realistic fixtures validate;
- no old `paths.yaml` or generator dependency exists.
