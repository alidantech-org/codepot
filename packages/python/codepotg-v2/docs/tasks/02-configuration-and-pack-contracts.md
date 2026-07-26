# Configuration and pack contract tasks

## CFG-001 — Location-aware document model

**Status:** planned

**Dependencies:** CORE-004

- [ ] Define immutable mapping, sequence, scalar, and null syntax nodes.
- [ ] Preserve source identity, line/column spans, document path, and original key text.
- [ ] Implement safe YAML and JSON parsers behind a document-loader port.
- [ ] Reject duplicate keys and unsafe/unregistered YAML tags.
- [ ] Add in-memory and file-backed parsing tests.

**Acceptance:** structural errors point to exact source locations and no raw loader object enters typed decoders.

## CFG-002 — Schema registry and typed decoder protocol

**Status:** planned

**Dependencies:** CFG-001, CORE-003

- [ ] Implement exact `(kind, apiVersion)` registration and resolution.
- [ ] Implement typed decoder, structural validator, semantic validator, serializer, and schema-introspection protocols.
- [ ] Detect duplicate schema registrations.
- [ ] Report unsupported kinds/versions without guessing.
- [ ] Prove no v1 `tasks` or `paths.yaml` fallback exists.

**Acceptance:** only documented v2 schema pairs decode.

## CFG-003 — Project root model

**Status:** planned

**Dependencies:** CFG-002

- [ ] Implement `apiVersion`, `kind`, metadata, `allow`, variables, and named sources.
- [ ] Implement source adapter ID and adapter-owned typed options container.
- [ ] Implement project units and root-relative path/value primitives.
- [ ] Reject unknown fields with suggestions.

**Tests:** full/empty optional sections, invalid IDs, unsafe paths, project-level `language`, `tasks`, and `templateDir` rejection.

## CFG-004 — Toolchains and security model

**Status:** planned

**Dependencies:** CFG-003

- [ ] Implement typed project toolchain selections and unit scoping.
- [ ] Implement project command policy, lifecycle-script policy, network/environment/filesystem requests.
- [ ] Keep host policy separate and authoritative.
- [ ] Add introspection metadata for configure/editor tooling.

**Acceptance:** project config can request but never grant capability beyond host policy.

## CFG-005 — Project commands

**Status:** planned

**Dependencies:** CFG-004

- [ ] Decode global project `before` and `after` command declarations.
- [ ] Implement structured executable/arguments/cwd/timeout/optional/permission fields.
- [ ] Reject implicit shell strings unless explicit shell mode is declared and permitted.
- [ ] Preserve command source spans.

## CFG-006 — Pack locator and pack-instance model

**Status:** planned

**Dependencies:** CFG-003

- [ ] Implement local path, GitHub shorthand, generic Git, and installed-distribution locator value objects.
- [ ] Implement ordered pack-instance IDs.
- [ ] Implement source, enabled, profile, output, clean, options, bindings, overrides, and project-owned commands.
- [ ] Implement project unit attachment.
- [ ] Validate duplicate IDs, missing sources, and unsafe output/clean paths.

**Acceptance:** same pack can be configured twice with independent instance values.

## PACKCFG-001 — Pack metadata, compatibility, and traits

**Status:** planned

**Dependencies:** CFG-002, CORE-003

- [ ] Implement pack ID/version/description/repository/license/docs metadata.
- [ ] Implement core, plugin API, IR, target adapter, and engine compatibility requirements.
- [ ] Implement composable integration traits: creates project, owns folder, contributes files, requires dependencies/bindings, runnable alone, manifest mode.
- [ ] Add schema introspection and examples.

## PACKCFG-002 — Content roots, ignore, and write policy

**Status:** planned

**Dependencies:** PACKCFG-001

- [ ] Implement one or more content roots.
- [ ] Implement inline ignore patterns and `.codepotgignore` references.
- [ ] Implement Gitignore-compatible matcher with negation and deterministic ordering.
- [ ] Implement default lifecycle and managed/protected/immutable root declarations.
- [ ] Ensure authoring docs/tasks/caches are not emitted unless under an intentional content root.

## PACKCFG-003 — Options, rules, bindings, dependencies, setup

**Status:** planned

**Dependencies:** PACKCFG-001, CFG-002

- [ ] Implement pack option schema definitions and values.
- [ ] Implement language and template-engine rule sections dispatched to installed adapters.
- [ ] Implement binding catalog with kind, target, required state, accepted sources, discovery, missing policy, docs, examples.
- [ ] Implement typed ecosystem dependency declarations.
- [ ] Implement setup summary, questions, detection hints, typed actions, manual steps, and pack commands.
- [ ] Implement override policy.

## PACKCFG-004 — Selections, patterns, files, profiles

**Status:** planned

**Dependencies:** PACKCFG-002, PLAN selection contracts

- [ ] Implement named selection declarations.
- [ ] Implement folder/file patterns with typed tokens and specificity.
- [ ] Implement exact file configuration modifying discovered descriptors.
- [ ] Implement roles: template, barrel, static, binary, partial, documentation.
- [ ] Implement output expressions, binding usage, includes, providers/requires, conditions, lifecycle, local rules, named outputs.
- [ ] Implement profiles selecting declared files/defaults.

## RULE-001 — Rule descriptors and typed patches

**Status:** planned

**Dependencies:** CFG-002

- [ ] Implement rule field descriptor and schema provider.
- [ ] Implement typed full-rule and patch protocols.
- [ ] Implement replace, append, prepend, union, merge-by-key, remove, reset-to-default, and not-overridable operations.
- [ ] Distinguish absent/set/remove/reset states without overloading `None`.
- [ ] Add property tests for deterministic merges.

## RULE-002 — Restrictions and provenance

**Status:** planned

**Dependencies:** RULE-001

- [ ] Apply adapter defaults, pack, template, project-global, project-pack, and project-template layers in fixed order.
- [ ] Record provenance for every final field.
- [ ] Apply host, adapter, pack, and project permission hierarchy.
- [ ] Implement `inspect rules` data model.

## BIND-001 — Binding values and validation

**Status:** planned

**Dependencies:** PACKCFG-003, language port

- [ ] Implement import, barrel, project path, package, namespace, text, text-file, value, package-name, artifact, and raw binding value models.
- [ ] Validate project values against pack catalog and target adapter capability.
- [ ] Implement binding groups and default barrels.
- [ ] Track exact template consumers.

## BIND-002 — Missing binding policy and configure hints

**Status:** planned

**Dependencies:** BIND-001, SETUP-001

- [ ] Implement prompt, placeholder, omit, skip-template, and error policies.
- [ ] Implement visible machine-detectable placeholders.
- [ ] Implement symbol/file/module discovery hints and ambiguous candidate handling.
- [ ] Implement strict readiness conversion.

## Acceptance gate

This task group is complete when:

- canonical project and pack examples decode into immutable models;
- schema introspection drives a configure test without hardcoded questions;
- unknown/forbidden fields and overrides produce source-spanned diagnostics;
- no raw dictionary deep merge exists;
- no old `tasks`/`paths.yaml` decoder exists;
- one pack instance can configure options, bindings, output, overrides, and commands entirely inside `codepotg.yaml`.
