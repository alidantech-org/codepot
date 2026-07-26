# TypeScript language-adapter implementation plan

This package implements TypeScript target syntax only. It must not contain Node project management, NestJS, Next.js, React, OpenAPI, Jinja, output writing, command execution, or pack selection.

## TS-001 — Package and plugin foundation

**Status:** planned

**Dependencies:** core PLUG-001..PLUG-004, public language port, version primitives

- [ ] Add isolated `pyproject.toml`, src-layout package, typing marker, README, license metadata, and test configuration.
- [ ] Register `typescript` factory in `codepotg.language_adapters`.
- [ ] Declare targets and extensions: `.ts`, `.tsx`, `.mts`, `.cts`; document declaration-file handling such as `.d.ts` while preserving the full output name.
- [ ] Declare plugin API, IR, core, and behavior versions.
- [ ] Declare capability metadata only for features actually implemented.
- [ ] Add import and architecture tests proving only public CodepotG APIs are used.

**Acceptance:** package installs independently and core remains importable when this distribution is absent.

## TS-002 — Typed rule schema

**Status:** planned

**Dependencies:** core RULE-001/002

Define immutable full rules, override patches, field descriptors, defaults, merge policies, hard restrictions, examples, and introspection for:

### Identifiers

- [ ] invalid-character replacement;
- [ ] leading-digit policy;
- [ ] reserved-word policy;
- [ ] escape/prefix/suffix behavior;
- [ ] Unicode policy;
- [ ] role-specific validation for type, value, property, parameter, enum member, namespace, and file stem.

### Naming

- [ ] case policy by semantic role;
- [ ] acronym handling;
- [ ] leading/trailing separator handling;
- [ ] file and test filename transforms.

### Files and modules

- [ ] `.ts`/`.tsx`/`.mts`/`.cts` conventions;
- [ ] ESM/CommonJS syntax capability metadata without owning Node manifests;
- [ ] module specifier extension policy;
- [ ] index resolution;
- [ ] path separator normalization.

### Imports

- [ ] relative, alias, module/package, project-path, barrel, default-barrel, and raw escape modes;
- [ ] named, default, namespace, side-effect, type-only, and aliased imports;
- [ ] grouping, ordering, quote style, semicolon policy where adapter-owned;
- [ ] deduplication and symbol-collision alias strategy;
- [ ] extension omission/preservation;
- [ ] path alias mapping and longest-match behavior.

### Exports

- [ ] named export, export-all, type-only export, default export where requested;
- [ ] export path resolution and stable ordering;
- [ ] authored-barrel descriptor rendering.

### Types

- [ ] primitive mapping;
- [ ] arrays/readonly arrays;
- [ ] records/maps;
- [ ] tuples;
- [ ] unions/intersections;
- [ ] generics;
- [ ] function types;
- [ ] object/type references;
- [ ] optional property versus nullable value;
- [ ] literal types;
- [ ] unknown/never/void behavior where semantically valid;
- [ ] date/binary/external type strategy as typed rules, not pack assumptions.

### Literals and comments

- [ ] string/template escaping;
- [ ] number/boolean/null/array/object literals;
- [ ] property quoting;
- [ ] line/block/documentation comments;
- [ ] safe comment terminator handling.

### Formatting metadata

- [ ] indentation/newline/trailing newline and stable separator metadata only where needed for adapter-rendered snippets;
- [ ] avoid becoming a general formatter.

**Prohibited shortcut:** accepting `dict[str, object]` or generic recursive merges.

**Acceptance:** schema introspection can generate complete configuration help and rejects every unknown rule path.

## TS-003 — Identifier and naming policies

**Status:** planned

**Dependencies:** TS-002

- [ ] Implement complete reserved-word set for supported TypeScript behavior version.
- [ ] Implement role-aware validity and escaping.
- [ ] Implement deterministic case transforms and acronym tests.
- [ ] Preserve semantic-name provenance in diagnostics.
- [ ] Add property tests for valid output and determinism.

## TS-004 — Type renderer

**Status:** planned

**Dependencies:** core IR type contract, TS-002

- [ ] Render every declared type capability.
- [ ] Preserve optional versus nullable distinction.
- [ ] Apply parentheses/precedence correctly for unions, intersections, arrays, functions, and generics.
- [ ] Resolve semantic references without reading templates or filesystem.
- [ ] Report unsupported IR types through typed diagnostics.

## TS-005 — Literal and comment renderer

**Status:** planned

- [ ] Implement deterministic literal rendering and escaping.
- [ ] Handle unsafe Unicode/control values according to rule policy.
- [ ] Implement comments and documentation comments without injection through terminators.
- [ ] Add focused edge-case fixtures.

## TS-006 — Module path resolver

**Status:** planned

**Dependencies:** binding/import public contracts

- [ ] Resolve real project paths relative to every planned output.
- [ ] Resolve configured aliases by longest matching project root.
- [ ] Preserve explicit module/package strings.
- [ ] Resolve default barrel and binding-group sources.
- [ ] Normalize separators and apply extension/index rules.
- [ ] Reject paths escaping the declared project/output context where appropriate.

## TS-007 — Import planner and renderer

**Status:** planned

**Dependencies:** TS-006

- [ ] Consume semantic import requests.
- [ ] Deduplicate symbols and module specifiers.
- [ ] Separate/merge type-only imports according to rules.
- [ ] Resolve named/default/namespace collisions deterministically.
- [ ] Assign stable aliases and report irreconcilable conflicts.
- [ ] Group/order imports.
- [ ] Render statements for template contexts.
- [ ] Warn for raw imports that cannot be relocated/validated.

## TS-008 — Export and authored barrel services

**Status:** planned

**Dependencies:** TS-006

- [ ] Render export descriptors supplied to authored barrel templates.
- [ ] Support export-all, named, aliased, and type-only forms.
- [ ] Deduplicate and order exports.
- [ ] Keep comments/custom content entirely in the pack's barrel template.

## TS-009 — Plugin adapter facade

**Status:** planned

**Dependencies:** TS-003..TS-008

- [ ] Implement the public language adapter protocol by composing focused policies.
- [ ] Accept immutable construction context and typed effective rules.
- [ ] Expose target descriptors, capabilities, render services, and diagnostics.
- [ ] Keep instances session-safe and free of mutable global caches.

## TS-010 — Shared conformance

**Status:** planned

**Dependencies:** TS-009, core PLUG-006

- [ ] Pass target/extension inference tests.
- [ ] Pass identifier, type, literal, comment, import/export, binding, rule, determinism, immutability, and session-isolation tests for declared capabilities.
- [ ] Add package-specific `.d.ts`, TSX, ESM/CJS syntax, type-only, alias, barrel, and collision tests.

## TS-011 — Documentation and release

**Status:** planned

- [ ] Document every rule field and default with examples.
- [ ] Document capability matrix and unsupported features.
- [ ] Add standalone installation and third-party pack examples.
- [ ] Build wheel/sdist and test compatibility bounds.
- [ ] Record behavior version and release checklist.

## Completion gate

The package is complete only when:

- it passes public language conformance;
- every declared rule is typed/introspectable/tested;
- imports work for relative paths, aliases, module strings, project paths, packages, and barrels;
- no framework, Node manifest, source, engine, writer, CLI, or command logic exists;
- neutral IR input remains immutable;
- output is deterministic.
