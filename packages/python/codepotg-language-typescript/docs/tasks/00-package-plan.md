# TypeScript target adapter implementation plan

This package detects and validates TypeScript targets and calculates module/path facts only. It must not contain source parsing, semantic-kernel extensions, generated TypeScript syntax, Node project management, frameworks, Jinja, output writing, command execution, or pack selection.

## TS-001 — Package and plugin foundation

**Status:** planned

**Dependencies:** core PLUG-001..PLUG-006, target adapter port, version primitives

- [ ] Add isolated `pyproject.toml`, src-layout package, typing marker, README, license metadata, and test configuration.
- [ ] Register the TypeScript target factory in `codepotg.language_adapters`.
- [ ] Declare `.ts`, `.tsx`, `.mts`, `.cts`, and documented declaration-file behavior while preserving complete output names.
- [ ] Declare plugin API, core, IR, selection/planning, and behavior compatibility.
- [ ] Declare only detection, validation, and module/path capabilities actually implemented.
- [ ] Add architecture tests proving only public CodepotG APIs are used.
- [ ] Add explicit tests prohibiting semantic/facet/selector registration and emitted source snippets.

**Acceptance:** package installs independently and core remains importable when this distribution is absent.

## TS-002 — Typed target option schema

**Status:** planned

**Dependencies:** core typed configuration/options contracts

Define immutable options, patches only where permitted, descriptors, defaults, validation, examples, restrictions, and introspection for:

### Target files

- [ ] target suffix/descriptor behavior;
- [ ] declaration filename validation such as `.d.ts`;
- [ ] invalid/reserved filename policy;
- [ ] path separator normalization.

### Candidate identifiers

- [ ] role-specific validation for type, value, property, parameter, enum member, namespace, and file stem candidates;
- [ ] reserved-word diagnostics;
- [ ] Unicode/invalid-character/leading-digit validation facts;
- [ ] optional explicit escaping-validation facts without automatic semantic renaming.

### Module paths

- [ ] relative and project-path calculation;
- [ ] configured alias matching;
- [ ] package/module strings;
- [ ] index resolution;
- [ ] module specifier extension policy;
- [ ] path containment and invalid-specifier diagnostics.

**Prohibited options:** generated naming roles, type mapping, literals, comments, imports/exports syntax, quote/semicolon/formatting style, decorators, validators, or framework behavior.

**Acceptance:** schema introspection documents every allowed option and rejects every unknown or syntax-rendering path.

## TS-003 — Target and extension resolver

**Status:** planned

**Dependencies:** TS-002

- [ ] Implement longest-known target suffix matching.
- [ ] Preserve full output names such as `.d.ts` after engine suffix removal.
- [ ] Distinguish TypeScript and TSX target descriptors where capabilities differ.
- [ ] Produce deterministic descriptor IDs and diagnostics for unsupported/ambiguous suffixes.

## TS-004 — Filename and identifier validation

**Status:** planned

**Dependencies:** TS-002

- [ ] Implement complete reserved-word/contextual-keyword catalog for the behavior version.
- [ ] Validate target filenames/stems and declared candidate identifier roles.
- [ ] Preserve semantic-name and template/expression provenance in diagnostics.
- [ ] Return immutable validation facts rather than renamed strings or source snippets.
- [ ] Add property tests for determinism and valid/invalid boundaries.

## TS-005 — Module path resolver

**Status:** planned

**Dependencies:** TS-002, planned artifact/path contracts

- [ ] Calculate relative module paths between already planned artifacts.
- [ ] Resolve configured aliases by longest matching project root.
- [ ] Preserve explicit package/module strings and validate them.
- [ ] Resolve project-path and authored barrel provider destinations.
- [ ] Normalize separators and apply extension/index facts.
- [ ] Reject escaping, invalid, or ambiguous paths.
- [ ] Never inspect template contents or choose output directories.

## TS-006 — Dependency module descriptors

**Status:** planned

**Dependencies:** TS-005, core PLAN-006/PLAN-007

- [ ] Consume immutable provider/consumer artifact and semantic dependency descriptors.
- [ ] Return module facts such as specifier, relative/package/alias classification, extension/index facts, and diagnostics.
- [ ] Preserve symbols, local dependency name, and semantic type-only/value-use facts supplied by core.
- [ ] Do not deduplicate, group, order, alias, quote, or render import/export statements.
- [ ] Do not return source-code snippets.

## TS-007 — Capability and compatibility facade

**Status:** planned

**Dependencies:** TS-003..TS-006

- [ ] Implement the public target adapter protocol by composing focused detection/validation/path services.
- [ ] Accept immutable construction context and typed options.
- [ ] Expose target descriptors, validation/path capabilities, behavior identity, and diagnostics.
- [ ] Keep instances session-safe and free of mutable global caches.
- [ ] Reject calls requesting unsupported syntax rendering.

## TS-008 — Shared conformance and negative boundaries

**Status:** planned

**Dependencies:** TS-007, core PLUG-006

- [ ] Pass target/extension inference tests.
- [ ] Pass filename/reserved-name/candidate-identifier validation tests.
- [ ] Pass relative, alias, package/module, project-path, index, and extension module-path tests.
- [ ] Pass typed option, determinism, immutability, and session-isolation tests.
- [ ] Add `.d.ts`, TSX, ESM/CJS path-fact, alias longest-match, and path collision cases.
- [ ] Prove the package contains no TypeRenderer, LiteralRenderer, CommentRenderer, ImportRenderer, ExportRenderer, validator/decorator renderer, or framework rule path.
- [ ] Prove it cannot extend the semantic kernel, selector registry, expression roots, or render context.

## TS-009 — Integration with authored templates

**Status:** planned

**Dependencies:** TS-008, Jinja engine, official TypeScript pack

- [ ] Provide planned dependency/module facts to a fixture template.
- [ ] Have the fixture template author TypeScript imports, exports, types, literals, comments, and operations directly.
- [ ] Validate generated filenames/module specifiers without modifying rendered text.
- [ ] Assert exact output changes when the template changes and unchanged output when adapter-internal representation changes without behavior change.
- [ ] Prove no adapter-generated line exists in the output.

## TS-010 — Documentation and release

**Status:** planned

- [ ] Document every target option, descriptor, path fact, and validation capability.
- [ ] Document the strict template-owned syntax boundary with examples.
- [ ] Document unsupported services explicitly.
- [ ] Add standalone installation and third-party pack examples.
- [ ] Build wheel/sdist and test compatibility bounds.
- [ ] Record behavior version and release checklist.

## Completion gate

The package is complete only when:

- it passes public target-adapter conformance;
- every declared option/capability is typed, introspectable, and tested;
- relative, alias, package/module, project-path, index, and extension facts are correct;
- candidate validation never mutates semantic names;
- templates author every TypeScript character;
- no source, framework, engine, writer, CLI, command, semantic-extension, or syntax-rendering logic exists;
- output/path behavior is deterministic and all inputs remain immutable.
