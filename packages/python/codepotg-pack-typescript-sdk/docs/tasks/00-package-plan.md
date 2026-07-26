# TypeScript SDK pack implementation plan

This package authors a new v2 TypeScript SDK pack. It may study existing generated outputs for requirements, but it does not parse old `paths.yaml`, import old pack code, or preserve hidden barrel/generator behavior.

## PACK-TS-001 — Package and provider foundation

**Status:** planned

**Dependencies:** stable pack-provider/public pack contracts

- [ ] Add isolated package metadata, package-data rules, README, license, and tests.
- [ ] Register installed-pack provider metadata if official packs are discoverable through Python distributions.
- [ ] Include `CodepotgPack.yaml`, templates, static/binary assets, partials, pack docs, and examples in wheel/sdist.
- [ ] Declare core, pack-schema, IR, TypeScript adapter, Jinja engine, and ecosystem compatibility.

## PACK-TS-002 — Manifest identity and traits

- [ ] Define metadata, compatibility, content roots, ignore rules, write policy, and override policy.
- [ ] Declare supported traits/profiles: standalone package, contributed files, modular SDK, monolithic single-file SDK where supported.
- [ ] Declare owned versus contributed `package.json` behavior by profile.
- [ ] Declare public setup documentation.

## PACK-TS-003 — Pack options

Define typed options with defaults, validation, docs, examples, and configure prompts for choices such as:

- [ ] modular versus monolithic profile;
- [ ] model/DTO/operation/client/error/docs/test generation toggles;
- [ ] client style and request function organization;
- [ ] serialization/date/binary strategies that are pack policy and map into supported TypeScript adapter rules or template branches;
- [ ] generated package name/version when the pack owns a package;
- [ ] example/test generation;
- [ ] optional framework-neutral hooks.

Do not expose internal template filenames as normal user options.

## PACK-TS-004 — Selections

- [ ] Define named selections for models, enums, DTOs, requests, responses, operations, resources/tags, errors, and aggregate project context.
- [ ] Define deterministic filters/order/grouping.
- [ ] Define artifact-derived selections for authored barrels and registries.
- [ ] Support complete aggregate context for one-file output.

## PACK-TS-005 — Template and static file inventory

Author new templates/files for:

- [ ] model and enum types;
- [ ] request/response DTOs;
- [ ] operation/request functions or client methods;
- [ ] API client/runtime interfaces;
- [ ] error types and response handling;
- [ ] shared type/util files;
- [ ] configuration/documentation files;
- [ ] optional examples/tests;
- [ ] authored `index.ts.jinja` and nested barrel templates;
- [ ] neutral/license/header partials;
- [ ] static `.gitignore`, `.env.example`, license, sample configs, fixture assets where appropriate;
- [ ] optional owned `package.json.jinja`, `tsconfig.json`, and other package assets by standalone profile.

Each file must have one descriptor; no root system `barrels` key is allowed.

## PACK-TS-006 — File patterns and profiles

- [ ] Use `filePatterns` for per-resource/module folder fan-out where useful.
- [ ] Prove static files under tokenized folders copy to every selected destination.
- [ ] Define modular, grouped, minimal, and monolithic profiles through declared file IDs.
- [ ] Ensure every template target is inferred from filename such as `.ts.jinja`, `.json.jinja`, `.md.jinja`.
- [ ] Use explicit targets only for ambiguous names such as `Dockerfile.jinja`.

## PACK-TS-007 — Binding catalog

Declare and document every project integration point, with exact template consumers:

- [ ] HTTP transport/client abstraction;
- [ ] authentication/token source;
- [ ] base URL/config provider;
- [ ] error mapping;
- [ ] logger;
- [ ] custom date/serialization helper;
- [ ] project-owned base model/client type if offered;
- [ ] package name or output namespace;
- [ ] artifact references to another pack where needed.

For each binding:

- [ ] define kind, target, required state, accepted sources, suggested symbol, discovery hints, missing policy, docs, examples;
- [ ] support module, projectPath, barrel/default-barrel, package, and raw escape where meaningful;
- [ ] allow one project barrel to satisfy several bindings;
- [ ] mark optional behavior so omitted bindings do not create unused imports.

## PACK-TS-008 — Language and engine rules

- [ ] Define pack-owned TypeScript defaults using only fields published by the TypeScript adapter.
- [ ] Define safe Jinja pack rules using only engine schema fields.
- [ ] Define exact override policy for aliases, import strategy, extension omission, naming, formatting metadata, and exposed template rules.
- [ ] Deny overrides that would break pack invariants.
- [ ] Do not use raw dictionary options or hidden filters to bypass adapter rules.

## PACK-TS-009 — Dependencies and manifests

- [ ] Declare typed Node runtime/development dependencies by feature/profile.
- [ ] Support npm, pnpm, and Yarn capabilities without hardcoded package-manager commands.
- [ ] For standalone package profile, own a complete package manifest through an authored template or typed owned-manifest contract.
- [ ] For contributed mode, use typed manifest contributions rather than replacing user `package.json`.
- [ ] Declare scripts/exports/workspace contributions where required.

## PACK-TS-010 — Setup, commands, and docs

- [ ] Define `codepotg configure` questions for options/bindings/package identity.
- [ ] Define detection hints for aliases, package name, candidate transport/auth/logger symbols, manifests, and package manager.
- [ ] Define typed optional actions for dependency ensure, ESLint unused-import fix, formatting, type checking, and tests.
- [ ] Mark command phases and capabilities.
- [ ] Add manual integration steps and pack setup docs.
- [ ] Ensure pack-owned downloaded commands require approval by default.

## PACK-TS-011 — Small contract fixtures

- [ ] Add minimal source/IR fixture producing one enum, model, request, response, operation, error, and barrel.
- [ ] Test modular output.
- [ ] Test monolithic single-file output.
- [ ] Test default barrel binding and project-path relative import.
- [ ] Test static files, partials, ignores, profiles, missing binding placeholder, and strict readiness.
- [ ] Test no duplicate output/descriptors.

## PACK-TS-012 — Realistic SDK project

- [ ] Generate an inspectable multi-resource SDK with package metadata, docs, examples, and tests.
- [ ] Validate TypeScript syntax/type checking using declared toolchain actions when available.
- [ ] Validate npm, pnpm, and Yarn planning; at least one complete install/build fixture must run in repository-supported environments.
- [ ] Record generated file inventory and intentional design decisions.

## PACK-TS-013 — Git and installed distribution

- [ ] Prove local directory pack resolution.
- [ ] Prove generic Git/GitHub subdirectory resolution and lock identity using controlled fixtures.
- [ ] Prove installed distribution package-data discovery.
- [ ] Prove command approval digest changes when pack content/command changes.

## PACK-TS-014 — Requirements comparison and release

- [ ] Inspect representative old outputs only to identify missing user requirements.
- [ ] Record intentional output differences; never add old runtime/manifest parser compatibility.
- [ ] Pass pack manifest, discovery, file, static, binding, rules, command, planner, writer, and integration suites.
- [ ] Build wheel/sdist and verify all pack data is included.
- [ ] Version and publish independently.

## Completion gate

- project users configure the pack only through one `packs.<instance>` entry;
- no project-level language or internal template knowledge is required;
- barrels are authored templates;
- static files copy by default;
- bindings/dependencies/setup/commands are fully documented;
- modular and monolithic fixtures are deterministic and validate;
- no old `paths.yaml` or pack implementation dependency exists.
