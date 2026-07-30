# Dart target adapter implementation plan

This package detects and validates Dart targets and calculates URI/path facts only. Flutter remains a template-pack concern. The adapter must not parse semantic sources, extend the kernel, render Dart syntax, select templates, plan destinations, write files, or execute commands.

PR #30 implemented most behavior available through the current public `TargetAdapter` port. The audited typed-option and artifact-inspection defects were repaired and the synchronized current-port release gates, including a real Dart SDK oracle, were completed on `chatgpt/codepotx-restart`. Broader planner/module and official-pack work remains explicitly blocked.

## DART-001 — Package and plugin foundation

**Status:** complete for the current public adapter port

- [x] Add isolated package metadata, src layout, typing marker, README, license, and tests.
- [x] Register `dart` in `dryv.language_adapters`.
- [x] Declare the `.dart` descriptor, behavior version, compatibility, and implemented capabilities.
- [x] Implement the immutable adapter facade.
- [x] Add architecture tests proving no Flutter, source, engine, writer, CLI, command, pack, private core, or old-generator dependency.
- [x] Prove no semantic/facet/selector registration or emitted source snippets.
- [x] Reproduce import and entry-point checks from real installed core/adapter wheels.

## DART-002 — Typed target option schema

**Status:** implemented; public project/pack option bridge remains blocked

- [x] Define immutable reserved-word, Unicode, privacy, package-name, and package-URI preference options.
- [x] Reject unknown fields in `from_mapping()`.
- [x] Validate decoded package names and boolean preference values.
- [x] Expose deterministic option introspection.
- [x] Validate direct constructor values with the same strictness as `from_mapping()`.
- [x] Reject raw strings/non-enum policy values and non-string package names deterministically.
- [x] Add direct-constructor negative tests for enum, package, boolean, and adapter option-object values.
- [ ] Decode project/pack options only after the public configuration bridge exists.

Prohibited options remain generated naming transforms, type/nullability rendering, literals, comments, directives, prefixes/combinators, annotations, serialization, formatting, and Flutter policy.

## DART-003 — Target resolver

**Status:** complete for the current public adapter port

- [x] Implement deterministic `.dart` target detection and validation.
- [x] Preserve the complete output filename after engine suffix removal.
- [x] Produce a stable target descriptor and unsupported-target diagnostics.

## DART-004 — Filename and identifier validation

**Status:** implemented for the current request contract; source provenance remains blocked

- [x] Implement behavior-versioned reserved, built-in, context-sensitive, and contextual keyword catalogs.
- [x] Validate type, enum, value, property, parameter, namespace, and file-stem candidates.
- [x] Preserve leading-underscore privacy semantics without renaming.
- [x] Validate `.dart` output paths, reserved names, traversal, absolutes, separators, and target mismatch.
- [x] Return diagnostics rather than renamed candidates or source snippets.
- [x] Add deterministic property/boundary fixtures.
- [x] Run representative fixtures against a real Dart SDK.
- [ ] Attach source spans after the public validation request exposes provenance.

## DART-005 — URI and project-path resolver

**Status:** complete for the current public adapter port

- [x] Calculate relative URIs between planned artifacts.
- [x] Build `package:<name>/<path>` only from explicit package name and `lib` root facts.
- [x] Preserve and validate explicit `dart:`, `package:`, and relative URIs.
- [x] Normalize separators and reject invalid/escaping/network/file URI paths.
- [x] Preserve actual provider filenames without hidden index/barrel rewriting.
- [x] Avoid filesystem inspection and output-directory selection.

## DART-006 — Dependency module descriptors

**Status:** partial and blocked by missing public planner/module facts

- [x] Return current `ModulePathFacts` for relative, package, and explicit URIs.
- [x] Preserve current/provider artifact fields available through the public port.
- [x] Avoid deduplication, prefixes, combinators, ordering, quoting, and directive rendering.
- [ ] Consume symbols, local dependency names, provider export/barrel roles, target metadata, and planner-owned paths after core exposes them.
- [ ] Return diagnostics instead of stable `ValueError` prefixes after `ModulePathFacts` gains a diagnostic channel.

## DART-007 — Adapter facade

**Status:** complete for the current public adapter port

- [x] Compose target, identifier, output-path, and URI services behind the public adapter protocol.
- [x] Accept immutable typed construction options.
- [x] Expose truthful descriptors, capabilities, and behavior identity.
- [x] Keep instances session-safe and free from mutable global caches or syntax rendering.

## DART-008 — Conformance and negative boundaries

**Status:** complete for the current public adapter port

- [x] Pass shared target-adapter conformance.
- [x] Cover file, reserved-name, identifier, privacy, relative URI, package URI, explicit URI, and escaping cases.
- [x] Cover deterministic options, immutability, and session isolation.
- [x] Prove no type/literal/comment/directive/annotation/formatter renderer exists.
- [x] Prove no Flutter, widget, state-management, Pub, build-runner, semantic-extension, selector, or context ownership.
- [x] Reproduce the complete suite against the synchronized real core checkout.
- [x] Close the real Dart SDK oracle.

## DART-009 — Integration with authored templates

**Status:** partial; package-local authored fixture exists, official integration blocked

- [x] Demonstrate that returned URI facts can be inserted into authored fixture syntax.
- [x] Prove the adapter returns no generated source line.
- [ ] Integrate with the official Jinja engine, planner dependency facts, and an official Dart pack after those contracts are available.
- [ ] Assert exact output through the official generation pipeline.

## DART-010 — Documentation and release

**Status:** complete for the current public adapter port

- [x] Document target options, descriptor, URI facts, language baseline, and template-owned syntax boundary.
- [x] Document relative and `package:` examples and unsupported services.
- [x] Add benchmark, oracle, distribution, and entry-point tooling.
- [x] Record the original implementation-harness evidence.
- [x] Fix strict direct option construction and adapter option-object validation.
- [x] Make wheel/sdist content inspection build fresh temporary artifacts and never conditionally skip.
- [x] Add exact installed distribution and semantic plugin-version assertions.
- [x] Run Ruff and formatting on the synchronized repository.
- [x] Run the complete real core and Dart suites.
- [x] Run the representative oracle against a real Dart SDK.
- [x] Build with the exact release command and install the real wheels in a fresh environment.
- [x] Require TypeScript and Dart entry points from freshly built wheels in a new `--no-index` virtual environment without a skip path.
- [x] Record final evidence and clean-tree status in `PROGRESS.md`.

## Audit follow-up

See:

- [`../audits/2026-07-27-pr-30-audit.md`](../audits/2026-07-27-pr-30-audit.md)
- [`AUDIT_FIXES.md`](AUDIT_FIXES.md)

## Completion gate

The current public-port release is complete because:

- shared conformance passes against the synchronized real core;
- every currently exposed option/capability is typed, introspectable, and equally validated through direct and mapping construction;
- relative, package, and explicit URI facts resolve from actual planned paths;
- candidate validation never mutates semantic names;
- representative behavior is verified by a real Dart SDK;
- templates author every Dart character;
- missing planner/symbol facts remain explicit blockers rather than private emulation;
- no Flutter/framework/ecosystem/source/engine/writer/command/semantic-extension/syntax-rendering logic exists;
- Ruff, format, full tests, build, SDK oracle, post-build artifact inspection, real-wheel installation, isolated dual-entry-point checks, and clean-tree checks pass and are recorded.

DART-006 and DART-009 are not release regressions. They are future integration tasks blocked by missing public contracts and must remain partial until those contracts exist.
