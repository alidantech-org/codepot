# Flutter application-integration pack implementation plan

Flutter is framework policy expressed entirely through pack templates. This package consumes the closed semantic kernel and Dart target path/validation facts. It must not extend semantics, duplicate target syntax rendering, or use old profile/file-pattern machinery.

## PACK-FLUTTER-001 — Package and provider foundation

**Status:** planned

- [ ] Add isolated package metadata, package-data rules, README, license, and tests.
- [ ] Include `CodepotgPack.yaml`, templates, static/binary assets, docs, partials, and examples.
- [ ] Declare compatibility with core, pack schema, IR/naming/selection behavior, Dart target adapter, Jinja engine, Dart ecosystem contracts, and supported Flutter/Dart toolchains.
- [ ] Add architecture tests proving no semantic-extension, target-syntax-renderer, or private-core access.

## PACK-FLUTTER-002 — One coherent integration product

- [ ] Define one host-application integration layer with deterministic generated file inventory.
- [ ] Define identity, compatibility, include/exclude, options, bindings, selections, executable defaults, and exact commands.
- [ ] Do not add standalone/existing-app/minimal/provider/monolithic profiles, file IDs, traits, or `filePatterns`.
- [ ] Treat materially different state-management, standalone-package, or interaction architectures as separate packs.

## PACK-FLUTTER-003 — Typed pack options

- [ ] Define generated namespace/client identity options.
- [ ] Define authored transport, authentication, error, base URL, serialization, and state integration strategies.
- [ ] Define view/navigation/form conventions supported by this pack product.
- [ ] Define docs/examples/test content options only when output remains intentional and deterministic.
- [ ] Add defaults, validation, documentation, examples, and configure prompts.
- [ ] Do not expose internal templates, selectors, semantic context, target-adapter render rules, or arbitrary dictionaries.

## PACK-FLUTTER-004 — Root-first selections and relationships

- [ ] Define `groups.schemas.enums.each` enum selection.
- [ ] Define `groups.schemas.objects.each` schema-type selection.
- [ ] Define `groups.each` group-client selection traversing `group.operations`.
- [ ] Define `groups.views.each` view selection.
- [ ] Link view trigger templates to declared operations through semantic identity.
- [ ] Define authored type/client/view/root export selections.
- [ ] Define generated dependencies through selection keys and declared symbols.
- [ ] Use documented `group`, `schema`, `operation`, `view`, `input`, `output`, and `failure` contexts only.
- [ ] Do not use model/resource/entity/service/frontend/UI/screen/page/component/widget selector roots or arbitrary queries.

## PACK-FLUTTER-005 — Template and static inventory

Author files for:

- [ ] Dart structural schema and enum types;
- [ ] serialization written by templates/macros;
- [ ] group API clients and operation calls;
- [ ] input/output/failure handling;
- [ ] declared Flutter views, parts, flows, and trigger-to-operation wiring;
- [ ] access-aware presentation branches supported by the pack;
- [ ] error, transport, configuration, and state abstractions;
- [ ] authored export templates;
- [ ] docs/examples/tests;
- [ ] syntax/license/header macros and partials;
- [ ] static analysis configuration, sample assets, fixtures, and documentation.

Every generated Dart/Flutter character is pack-authored. No hidden export, widget, navigation, or state-generation subsystem exists in core or the Dart adapter.

## PACK-FLUTTER-006 — Filesystem layout and target inference

- [ ] Use `{selectionKey}` folders for schemas, groups, and views.
- [ ] Use `(expression)` names in `x.name.{casing}.{number}` order.
- [ ] Infer `.dart`, `.yaml`, `.md`, and other targets from filenames.
- [ ] Prove selection-scoped static files fan out and ordinary static assets copy unchanged.
- [ ] Validate no duplicate descriptor/destination.
- [ ] Do not add profiles or `filePatterns`.

## PACK-FLUTTER-007 — Binding catalog

Declare/document exact template consumers for:

- [ ] HTTP transport or project network abstraction;
- [ ] authentication token source;
- [ ] base URL/environment provider;
- [ ] error mapper;
- [ ] logging;
- [ ] project package/module identity;
- [ ] state/navigation integration abstractions used by this product;
- [ ] explicit artifacts from another pack.

For every binding:

- [ ] define typed kind, required state, docs/examples, and missing policy;
- [ ] support package URI, project path, relative URI, explicit URI, text/value, or artifact facts where meaningful;
- [ ] list exact selection/template consumers;
- [ ] keep generated dependencies separate under selection `imports`/`exports`;
- [ ] ensure templates author all import/integration syntax.

## PACK-FLUTTER-008 — Template-owned Dart and Flutter conventions

- [ ] Author Jinja macros/partials for Dart types, nullability, literals, comments, annotations, imports, exports, serialization, and formatting.
- [ ] Author Flutter widgets, layouts, routes, navigation, forms, state wiring, trigger handlers, and access presentation in templates.
- [ ] Use core naming projections directly.
- [ ] Consume Dart adapter facts only for suffix, candidate validation, and URI/path calculation.
- [ ] Reject TypeRenderer, ImportRenderer, language naming APIs, or pre-rendered adapter snippets.
- [ ] Keep all framework policy inside this pack product.

## PACK-FLUTTER-009 — Host project contributions and exact commands

- [ ] Declare typed known Flutter/Dart dependency and asset contributions where ecosystem contracts support them.
- [ ] Do not replace unrelated host project content.
- [ ] Express pub get, build runner, format, analyze, and tests as exact optional commands.
- [ ] Declare approvals, capabilities, and command phases.
- [ ] Store generated output state outside the dependency lock.

## PACK-FLUTTER-010 — Small connected fixture

- [ ] Add one group with enum/object schemas, operations, and one declared view with trigger-to-operation relationship.
- [ ] Generate types, group client, view, errors, and authored exports.
- [ ] Test semantic provider matching, URI facts, and view-operation resolution.
- [ ] Test template-authored Dart/Flutter syntax byte-for-byte.
- [ ] Test static files, partials, ignores, bindings, missing policies, and strict readiness.
- [ ] Test no removed vocabulary/selectors or duplicate descriptors.

## PACK-FLUTTER-011 — Realistic host application fixture

- [ ] Generate into a controlled existing Flutter application.
- [ ] Include several groups, schemas, operations, views, flows, triggers, access facts, and related events where supported.
- [ ] Plan typed dependency/assets contributions.
- [ ] Run format/analyze/tests through declared commands in supported environments.
- [ ] Assert artifact explain traces and schema/operation/view blast radius.
- [ ] Prove the project user does not need internal template knowledge.
- [ ] Prove all generated text originates in templates/macros or semantic facts.

## PACK-FLUTTER-012 — Resolution, distribution, and release

- [ ] Prove local, Git subdirectory, lock, installed distribution, and digest-bound command approval behavior.
- [ ] Inspect old outputs only for requirements and document intentional differences.
- [ ] Never implement old pack/config compatibility.
- [ ] Pass manifest, discovery, selection, dependency, view relationship, template, static, binding, ecosystem, command, security, impact, and integration suites.
- [ ] Build wheel/sdist with all pack data and publish independently.

## Completion gate

- Flutter remains one framework pack product using the Dart adapter for validation/path facts only;
- schemas, groups, operations, and views use closed-kernel root-first selectors;
- views are generated only from declared view semantics;
- templates author every Dart/Flutter statement, widget, route, and export;
- dependencies, bindings, contributions, and exact commands are documented and secure;
- realistic host fixture validates and impact output is deterministic;
- no old `paths.yaml`, profiles, file patterns, frontend/UI roots, model/resource/entity contexts, semantic extension, or old generator dependency exists.
