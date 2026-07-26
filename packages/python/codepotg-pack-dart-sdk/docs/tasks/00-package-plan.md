# Dart SDK pack implementation plan

This package authors one standalone modular v2 Dart SDK pack. It consumes the closed semantic kernel through root-first fixed selectors and authors every Dart character in templates/macros/partials. It does not parse old pack files, add semantic extensions, use hidden profiles, or rely on target-adapter syntax renderers.

## PACK-DART-001 — Package and provider foundation

**Status:** planned

- [ ] Add isolated package metadata, package-data rules, README, license, and tests.
- [ ] Include `CodepotgPack.yaml`, templates, static/binary assets, partials, docs, and examples in wheel/sdist.
- [ ] Declare core, pack-schema, IR/naming/selection behavior, Dart target adapter, Jinja engine, and Dart project compatibility.
- [ ] Add architecture tests proving no semantic-extension/private-core access.

## PACK-DART-002 — One coherent manifest product

- [ ] Define one standalone modular SDK package with owned `pubspec.yaml`, analysis config, docs, examples, library files, and deterministic output inventory.
- [ ] Define identity, compatibility, include/exclude, options, bindings, selections, executable defaults, and exact commands.
- [ ] Do not add standalone/contribution/modular/monolithic profiles, file IDs, or `filePatterns`.
- [ ] Treat existing-project contribution, Flutter integration, or materially different single-file output as separate packs.

## PACK-DART-003 — Typed pack options

- [ ] Define package/client identity options.
- [ ] Define authored serialization, transport, date/binary, and error/result strategies.
- [ ] Define examples/docs/test content options only where file output remains intentional and deterministic.
- [ ] Add validation, defaults, documentation, examples, and configure prompts.
- [ ] Do not expose internal templates, selectors, semantic context, target-adapter render rules, or arbitrary dictionaries.

## PACK-DART-004 — Root-first selections

- [ ] Define `groups.schemas.enums.each` enum selection.
- [ ] Define `groups.schemas.objects.each` schema-type selection.
- [ ] Define `groups.each` group-client selection traversing `group.operations`.
- [ ] Define authored types/client/package export selections through `exports`.
- [ ] Define generated dependencies through selection keys and declared symbols.
- [ ] Use documented `group`, `schema`, `operation`, `input`, `output`, and `failure` contexts only.
- [ ] Do not use model/resource/entity/service/request/response selector roots or arbitrary queries.

## PACK-DART-005 — Template and static inventory

Author files for:

- [ ] structural schema/enums and JSON serialization;
- [ ] group clients and operation calls;
- [ ] input/output/failure handling;
- [ ] errors and transport abstractions;
- [ ] shared utilities/configuration;
- [ ] authored export templates;
- [ ] docs/examples/tests;
- [ ] syntax/license/header macros and partials;
- [ ] static analysis configuration, license, fixtures, and assets;
- [ ] owned `pubspec.yaml.jinja` and package files.

All Dart types, nullability, imports, exports, literals, comments, annotations, serialization, and formatting are pack-authored. No hidden export subsystem is allowed.

## PACK-DART-006 — Filesystem layout and target inference

- [ ] Use `{selectionKey}` folders for schema/group fan-out.
- [ ] Use naming expressions in `x.name.{casing}.{number}` order.
- [ ] Infer Dart, YAML, Markdown, and other targets from filenames.
- [ ] Prove static files copy unchanged and selection-scoped static files fan out correctly.
- [ ] Validate no duplicate descriptor/destination.
- [ ] Do not add profiles or `filePatterns`.

## PACK-DART-007 — Binding catalog

Declare/document exact consumers for:

- [ ] HTTP transport/client;
- [ ] authentication/token provider;
- [ ] base URL/configuration;
- [ ] error mapper;
- [ ] logger;
- [ ] package/module identity;
- [ ] serialization helpers or project abstractions;
- [ ] explicit artifacts from other packs.

For every binding:

- [ ] define typed kind, required state, docs/examples, and missing policy;
- [ ] support package URI, project path, relative URI, explicit URI, text/value, or artifact facts where meaningful;
- [ ] list exact selection/template consumers;
- [ ] separate generated dependencies under `imports`/`exports`;
- [ ] ensure templates author URI/import/export syntax.

## PACK-DART-008 — Template-owned Dart conventions

- [ ] Author Jinja macros/partials for Dart types, nullability, literals, comments, annotations, imports, exports, prefixes/combinators, serialization, and formatting.
- [ ] Use core naming projections directly.
- [ ] Consume Dart target adapter facts only for suffix, candidate validation, and URI/path calculation.
- [ ] Define pack options/branches for supported conventions.
- [ ] Reject TypeRenderer, ImportRenderer, language naming APIs, or pre-rendered adapter snippets.
- [ ] Keep Flutter widgets/state/layout outside this pack.

## PACK-DART-009 — Package files and exact commands

- [ ] Author complete `pubspec.yaml.jinja`, package library/export files, README, analysis configuration, and static files.
- [ ] Express pub get, build runner, format, analyze, and tests as exact optional commands.
- [ ] Keep package-manager intelligence outside semantic core.
- [ ] Ensure downloaded commands require approval by default.
- [ ] Store output digests in ownership state rather than dependency lock.

## PACK-DART-010 — Small connected fixture

- [ ] Add one group with enum/object schemas and operations containing inputs, outputs, failures, effects, and HTTP facets.
- [ ] Generate schema types, a group client, errors, package files, and authored exports.
- [ ] Test semantic provider matching and URI facts.
- [ ] Test template-authored Dart syntax byte-for-byte.
- [ ] Test static files, partials, ignores, bindings, missing policies, and strict readiness.
- [ ] Test no removed vocabulary/selectors or duplicate descriptors.

## PACK-DART-011 — Realistic standalone package

- [ ] Generate an inspectable multi-group API SDK with pubspec, docs, examples, analysis config, and tests.
- [ ] Run format/analyze/tests through declared commands where supported.
- [ ] Validate relative/package URI paths.
- [ ] Assert artifact explain traces and schema/operation blast radius.
- [ ] Prove all generated text originates in templates/macros or semantic facts.

## PACK-DART-012 — Resolution, distribution, and release

- [ ] Prove local, Git subdirectory, locked commit, and installed distribution pack resolution.
- [ ] Prove approval digest changes with pack content/command changes.
- [ ] Inspect old outputs only for requirements and document intentional differences.
- [ ] Never add old pack/config compatibility.
- [ ] Pass manifest, discovery, selection, dependency, template, static, binding, command, planner, impact, writer, and integration suites.
- [ ] Build wheel/sdist with all pack data and publish independently.

## Completion gate

- one standalone modular product works through the v2 manifest only;
- all selectors are group-rooted and closed-kernel;
- templates author every Dart statement and export;
- target adapter provides validation/URI facts only;
- bindings and exact commands are documented;
- realistic package validates and impact output is deterministic;
- no old `paths.yaml`, profiles, file patterns, model/resource/entity contexts, semantic extension, or old generator dependency exists.
