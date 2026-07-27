# TypeScript target adapter implementation plan

This package detects and validates TypeScript targets and calculates module/path facts only. It must not contain source parsing, semantic-kernel extensions, generated TypeScript syntax, Node project management, frameworks, Jinja, output writing, command execution, or pack selection.

PR #30 implemented most behavior available through the current public `TargetAdapter` port. The audited typed-option and artifact-inspection defects were repaired and the synchronized current-port release gates were completed on `chatgpt/codepotx-restart`. Broader planner/module and official-pack work remains explicitly blocked.

## TS-001 — Package and plugin foundation

**Status:** complete for the current public adapter port

- [x] Add isolated package metadata, src layout, typing marker, README, license, and tests.
- [x] Register `typescript` in `codepotg.language_adapters`.
- [x] Declare `.ts`, `.tsx`, `.mts`, `.cts`, `.d.ts`, `.d.mts`, and `.d.cts` behavior.
- [x] Declare public plugin/API/IR compatibility and implemented capabilities.
- [x] Add architecture tests proving public-only CodepotG usage and no syntax-rendering ownership.
- [x] Reproduce package import and entry-point checks from real installed core/adapter wheels.

## TS-002 — Typed target option schema

**Status:** implemented; public project/pack option bridge remains blocked

- [x] Define immutable reserved-word, Unicode, extension, index, package, and alias options.
- [x] Reject unknown fields in `from_mapping()`.
- [x] Validate package and alias syntax, ordering, duplicates, and ambiguity for decoded values.
- [x] Validate direct constructor values with the same strictness as `from_mapping()`.
- [x] Reject raw strings/non-enum policy values and non-string package names deterministically.
- [x] Add direct-constructor negative tests for policy, package, alias collection, and alias item types.
- [ ] Decode project/pack options only after the public configuration bridge exists.

Prohibited options remain generated naming roles, type mapping, literals, comments, import/export syntax, quote/semicolon/formatting style, decorators, validators, and framework behavior.

## TS-003 — Target and extension resolver

**Status:** complete for the current public adapter port

- [x] Implement longest-known target suffix matching.
- [x] Preserve complete declaration suffix identity.
- [x] Distinguish TypeScript and TypeScript-JSX descriptors.
- [x] Produce deterministic descriptors and target mismatch diagnostics.

## TS-004 — Filename and identifier validation

**Status:** implemented for the current request contract; source provenance remains blocked

- [x] Implement a behavior-versioned reserved/contextual-word catalog.
- [x] Validate type, value, property, parameter, enum member, namespace, and file-stem candidates.
- [x] Validate target paths, declaration filenames, reserved names, traversal, absolute paths, separators, and target mismatch.
- [x] Return diagnostics without renaming candidates.
- [x] Add deterministic boundary/property and TypeScript compiler-oracle fixtures.
- [ ] Attach semantic/template source spans after the public request contract exposes provenance.

## TS-005 — Module path resolver

**Status:** complete for the current public adapter port

- [x] Calculate relative module paths between planned artifacts.
- [x] Resolve aliases by longest complete path-segment root.
- [x] Validate package names and explicit module specifiers.
- [x] Apply explicit extension and index policies.
- [x] Normalize separators and reject invalid/escaping/ambiguous paths.
- [x] Avoid filesystem inspection and output-directory selection.

## TS-006 — Dependency module descriptors

**Status:** partial and blocked by missing public planner/module facts

- [x] Return current `ModulePathFacts` for relative, alias, package, and explicit paths.
- [x] Preserve current/provider artifact fields available through the port.
- [x] Avoid grouping, ordering, aliasing symbols, or rendering imports/exports.
- [ ] Consume symbols, local dependency name, semantic type-only/value-use facts, provider export/barrel role, and planner-owned aliases after core exposes them.
- [ ] Return diagnostics instead of stable `ValueError` prefixes after `ModulePathFacts` gains a diagnostic channel.

## TS-007 — Capability and compatibility facade

**Status:** complete for the current public adapter port

- [x] Compose descriptors, identifier validation, path validation, and module resolution behind the public adapter protocol.
- [x] Accept immutable typed construction options.
- [x] Expose truthful capabilities and behavior identity.
- [x] Keep instances free of mutable global caches and rendering behavior.

## TS-008 — Shared conformance and negative boundaries

**Status:** complete for the current public adapter port

- [x] Pass public target-adapter conformance.
- [x] Cover target, extension, declaration, filename, reserved-name, and identifier validation.
- [x] Cover relative, alias, package, explicit, index, extension, and escaping cases.
- [x] Cover deterministic options, immutability, and session isolation.
- [x] Prove no type/literal/comment/import/export/validator/decorator/framework renderer exists.
- [x] Prove no semantic/facet/selector/context extension exists.
- [x] Reproduce the complete suite against the synchronized real core checkout.

## TS-009 — Integration with authored templates

**Status:** partial; package-local authored fixture exists, official integration blocked

- [x] Demonstrate that returned module facts can be inserted into authored fixture syntax.
- [x] Prove the adapter returns no generated source line.
- [ ] Integrate with the official Jinja engine, planner dependency facts, and an official TypeScript pack after those contracts are available.
- [ ] Assert exact rendered output changes through the official generation pipeline.

## TS-010 — Documentation and release

**Status:** complete for the current public adapter port

- [x] Document current descriptors, options, module facts, baseline, and template-owned syntax boundary.
- [x] Document explicit unsupported services.
- [x] Add benchmark, oracle, distribution, and combined entry-point tooling.
- [x] Record the original implementation-harness evidence.
- [x] Fix strict direct option construction and adapter option-object validation.
- [x] Make wheel/sdist content inspection build fresh temporary artifacts and never conditionally skip.
- [x] Add exact installed distribution and semantic plugin-version assertions.
- [x] Run Ruff and formatting on the synchronized repository.
- [x] Run the complete real core and TypeScript suites.
- [x] Run the TypeScript compiler oracle with TypeScript 5.9-compatible Node 16 module settings.
- [x] Build with the exact release command and install the real wheels in a fresh environment.
- [x] Require TypeScript and Dart entry points from freshly built wheels in a new `--no-index` virtual environment without a skip path.
- [x] Record final evidence and clean-tree status in `PROGRESS.md`.

## Audit follow-up

See:

- [`../audits/2026-07-27-pr-30-audit.md`](../audits/2026-07-27-pr-30-audit.md)
- [`AUDIT_FIXES.md`](AUDIT_FIXES.md)

## Completion gate

The current public-port release is complete because:

- it passes public conformance against the synchronized real core;
- every currently exposed option/capability is typed, introspectable, and equally validated through direct and mapping construction;
- relative, alias, package, explicit, index, extension, and declaration facts are correct;
- candidate validation never mutates semantic names;
- templates author every TypeScript character;
- missing planner/symbol facts remain explicit blockers rather than private emulation;
- no source, framework, engine, writer, CLI, command, semantic-extension, or syntax-rendering logic exists;
- Ruff, format, full tests, build, compiler oracle, post-build artifact inspection, real-wheel installation, isolated dual-entry-point checks, and clean-tree checks pass and are recorded.

TS-006 and TS-009 are not release regressions. They are future integration tasks blocked by missing public contracts and must remain partial until those contracts exist.
