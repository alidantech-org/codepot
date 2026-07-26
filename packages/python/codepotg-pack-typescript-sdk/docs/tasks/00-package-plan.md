# TypeScript SDK pack implementation plan

This package authors one modular v2 TypeScript SDK pack. It consumes the closed semantic kernel through root-first fixed selectors and authors every TypeScript character in templates/macros/partials. It does not parse old `paths.yaml`, import old pack code, extend the kernel, or depend on language-adapter syntax renderers.

## PACK-TS-001 — Package and provider foundation

**Status:** planned

**Dependencies:** stable pack-provider/public pack contracts

- [ ] Add isolated package metadata, package-data rules, README, license, and tests.
- [ ] Register installed-pack metadata if official packs are discoverable through Python distributions.
- [ ] Include `CodepotgPack.yaml`, templates, static/binary assets, partials, pack docs, and examples in wheel/sdist.
- [ ] Declare core, pack-schema, IR/naming/selection behavior, TypeScript target adapter, Jinja engine, and Node project compatibility.
- [ ] Add architecture tests proving the pack has no semantic-extension or private-core access.

## PACK-TS-002 — One coherent manifest product

- [ ] Define root identity, compatibility, include/exclude rules, options, bindings, selections, executable defaults, and exact commands.
- [ ] Produce one modular SDK product with deterministic file inventory.
- [ ] Do not add root profiles, file IDs, `filePatterns`, write-policy matrices, or hidden product activation.
- [ ] Treat materially different monolithic/framework/contribution products as separate future packs.
- [ ] Add public setup documentation.

## PACK-TS-003 — Typed pack options

Define documented typed options only where authored templates can vary output without changing the semantic kernel or hidden file inventory:

- [ ] client name;
- [ ] client method/function organization;
- [ ] transport abstraction choice among pack-authored branches;
- [ ] date/binary/serialization representation;
- [ ] error/result strategy;
- [ ] optional examples/docs content where files remain valid and intentional;
- [ ] package identity values used by authored package templates.

Do not expose internal filenames, selectors, semantic contexts, language-adapter render rules, or arbitrary dictionaries.

## PACK-TS-004 — Root-first selections

- [ ] Define `groups.schemas.enums.each` enum selection.
- [ ] Define `groups.schemas.objects.each` schema-type selection.
- [ ] Define `groups.each` group-client selection whose templates traverse `group.operations`.
- [ ] Define authored types/client/root barrel selections through ordered `exports`.
- [ ] Define explicit generated dependencies through selection keys and declared symbols.
- [ ] Use only context roots such as `group`, `schema`, `operation`, `input`, `output`, and `failure`.
- [ ] Do not use neutral model/resource/entity/service/request/response selector roots.
- [ ] Do not add arbitrary filtering/query DSLs.

## PACK-TS-005 — Template and static inventory

Author new files for:

- [ ] structural schema and enum types;
- [ ] group-scoped client classes/functions iterating operations;
- [ ] operation input/output/failure handling;
- [ ] HTTP request construction from `operation.facets.http`;
- [ ] API client/runtime interfaces;
- [ ] error/result abstractions;
- [ ] shared authored utilities/configuration;
- [ ] authored nested and root barrel templates;
- [ ] package/configuration/documentation files;
- [ ] optional examples/tests where included in this coherent product;
- [ ] neutral/license/header and syntax macros/partials;
- [ ] static configuration/assets where appropriate.

Every emitted character, including types/imports/exports/comments/literals/HTTP calls, is pack-authored. Each discovered file has one descriptor; no root barrel subsystem exists.

## PACK-TS-006 — Filesystem layout and target inference

- [ ] Use `{selectionKey}` folders for schema/group fan-out.
- [ ] Use `(expression)` with `x.name.{casing}.{number}` for filenames.
- [ ] Prove static files under selection folders fan out without rendering.
- [ ] Infer `.ts`, `.tsx`, `.json`, `.md`, and other targets from filenames.
- [ ] Use `{root}` only when physical authoring layout should not create an output folder.
- [ ] Validate no duplicate descriptors/destinations.
- [ ] Do not add profiles or `filePatterns`.

## PACK-TS-007 — Binding catalog

Declare/document exact template consumers for external integration points such as:

- [ ] HTTP transport/client abstraction;
- [ ] authentication/token source;
- [ ] base URL/config provider;
- [ ] error mapping;
- [ ] logger;
- [ ] custom serialization helpers;
- [ ] package/module identity;
- [ ] explicit artifacts from another pack where required.

For each binding:

- [ ] define typed kind, required state, accepted sources, docs, examples, and missing policy;
- [ ] support module, project path, package, namespace, text/value, and artifact facts where meaningful;
- [ ] list exact selection/template consumers;
- [ ] keep generated selection dependencies separate under `imports`/`exports`;
- [ ] ensure templates author all binding/import syntax.

## PACK-TS-008 — Template-owned TypeScript conventions

- [ ] Author Jinja macros/partials for TypeScript type expressions, identifier placement, optional/nullable syntax, literals, comments, imports, exports, and formatting.
- [ ] Use core naming projections directly in the approved order.
- [ ] Consume TypeScript target adapter facts only for suffix, filename/identifier validation, and module specifiers.
- [ ] Define pack options/branches for supported conventions.
- [ ] Reject reliance on TypeRenderer, ImportRenderer, language naming APIs, or pre-rendered adapter snippets.
- [ ] Keep NestJS/React/Next.js/framework conventions outside this framework-neutral SDK pack.

## PACK-TS-009 — Package files and exact commands

- [ ] Author complete `package.json.jinja`, `tsconfig.json`, README, and static package files for this pack product.
- [ ] Express dependency installation/format/typecheck/test behavior as exact optional commands with opaque arguments.
- [ ] Keep package-manager intelligence outside semantic core.
- [ ] Ensure downloaded commands require approval by default.
- [ ] Record package/output digests in ownership state, not the dependency lock.

## PACK-TS-010 — Small connected fixture

- [ ] Add one group with enum/object schemas and operations containing inputs, outputs, failures, effects, and HTTP facets.
- [ ] Generate schema types, a group client, errors, package files, and authored barrels.
- [ ] Test semantic dependency matching and module facts.
- [ ] Test template-authored imports/exports/types byte-for-byte.
- [ ] Test static files, partials, ignores, bindings, missing policies, and strict readiness.
- [ ] Test no duplicate output/descriptors and no removed vocabulary/selectors.

## PACK-TS-011 — Realistic SDK project

- [ ] Generate an inspectable multi-group SDK with package metadata, docs, examples, and tests.
- [ ] Validate TypeScript syntax/type checking through declared commands when available.
- [ ] Assert exact artifact explain traces and schema/operation blast radius.
- [ ] Record generated inventory and intentional pack conventions.
- [ ] Prove all generated text changes originate in templates/macros or semantic input facts.

## PACK-TS-012 — Resolution, distribution, and release

- [ ] Prove local directory, generic Git subdirectory, lock identity, and installed distribution resolution.
- [ ] Prove command approval digest changes when pack content/command changes.
- [ ] Inspect representative old outputs only to identify requirements and document intentional differences.
- [ ] Never add old runtime/manifest parser compatibility.
- [ ] Pass manifest, discovery, selection, semantic dependency, template, static, binding, command, planner, impact, writer, and integration suites.
- [ ] Build wheel/sdist with complete pack data and publish independently.

## Completion gate

- the project config contains one direct pack instance and no global language/profile/internal template list;
- all selections are closed-kernel and group-rooted;
- barrels and every TypeScript statement are authored templates;
- target adapter provides validation/path facts only;
- static files copy by default;
- bindings and exact commands are fully documented;
- realistic output validates and blast-radius reports are deterministic;
- no old `paths.yaml`, profiles, file patterns, resource/model/entity contexts, semantic extension, or old pack implementation dependency exists.
