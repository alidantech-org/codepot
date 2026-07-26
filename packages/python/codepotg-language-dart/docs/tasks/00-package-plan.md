# Dart language-adapter implementation plan

This package implements Dart target syntax only. Flutter remains a framework/template-pack concern and must not appear as a Dart language alias or hidden behavior.

## DART-001 — Package and plugin foundation

**Status:** planned

**Dependencies:** core plugin/language ports and version primitives

- [ ] Add isolated package metadata, src layout, typing marker, README, and test configuration.
- [ ] Register `dart` in `codepotg.language_adapters`.
- [ ] Declare `.dart` target descriptor, behavior version, plugin/core/IR compatibility, and actual capabilities.
- [ ] Implement immutable adapter factory/context.
- [ ] Add architecture tests proving no Flutter, source, engine, writer, CLI, filesystem, command, or pack dependency.

## DART-002 — Typed rule schema

**Status:** planned

Define immutable full rules, patches, field descriptors, defaults, merge policy, restrictions, examples, and introspection for:

### Identifiers and naming

- [ ] reserved words and contextual keywords;
- [ ] role-specific identifiers for classes, enums, variables, fields, parameters, libraries, prefixes, and files;
- [ ] casing/acronyms/invalid-character/leading-digit policy;
- [ ] private-name underscore policy.

### Files and libraries

- [ ] `.dart` file naming;
- [ ] library/part conventions as capabilities, without assuming a specific pack uses them;
- [ ] URI path normalization;
- [ ] source package identity inputs.

### Imports and exports

- [ ] relative URI, `package:`, project-path, explicit URI, default project barrel/export binding, and raw escape modes;
- [ ] prefix (`as`), deferred, `show`, and `hide` combinators;
- [ ] ordering/grouping and quote policy;
- [ ] duplicate URI and prefix conflict handling;
- [ ] export directives and combinators.

### Types and null safety

- [ ] core primitives;
- [ ] lists, sets, maps, records, tuples where represented, generics, functions, futures, streams, and semantic references;
- [ ] nullable types;
- [ ] required named parameter semantics where requested by generation context;
- [ ] `dynamic`, `Object`, `Object?`, `Never`, `void`, and unsupported-type diagnostics;
- [ ] external/date/binary strategy as typed rules.

### Literals, comments, and annotations

- [ ] string/raw/multiline escaping;
- [ ] number, boolean, null, list, set, map, and record literals;
- [ ] line/block/documentation comments;
- [ ] annotation rendering only for language-level annotation descriptors, not Flutter/framework assumptions.

### Formatting metadata

- [ ] indentation/newline/trailing newline for adapter-generated snippets;
- [ ] no replacement for `dart format`.

**Acceptance:** schema introspection documents all supported fields and unknown paths are errors.

## DART-003 — Identifier and naming policies

- [ ] Implement reserved-word handling and role-aware validity.
- [ ] Implement deterministic file/type/member naming and acronym behavior.
- [ ] Add property tests proving valid output and stable transforms.

## DART-004 — Type renderer

- [ ] Render every declared IR capability with correct precedence.
- [ ] Preserve optional presence versus nullable type.
- [ ] Render functions, generics, records, collection types, futures, streams, and references.
- [ ] Report unsupported constructs rather than guessing.

## DART-005 — Literal/comment renderer

- [ ] Implement deterministic Dart literals and safe escaping.
- [ ] Implement documentation comments and comment terminator safety.
- [ ] Add raw/multiline string edge cases.

## DART-006 — URI and project-path resolver

- [ ] Calculate relative URIs between planned artifacts.
- [ ] Build `package:<name>/<path>` URIs from project package-name binding and actual project paths.
- [ ] Preserve explicit package/URI strings.
- [ ] Resolve default export/barrel binding groups.
- [ ] Normalize separators and reject invalid/escaping paths.

## DART-007 — Import planner

- [ ] Consume semantic imports.
- [ ] Deduplicate identical URIs and combinators.
- [ ] Assign deterministic prefixes for conflicts.
- [ ] Merge or separate `show`/`hide` according to typed policy.
- [ ] Support deferred imports only when declared by the request/capability.
- [ ] Order directives deterministically.
- [ ] Warn for raw imports.

## DART-008 — Export planner and authored export templates

- [ ] Render export descriptors for authored barrel/export templates.
- [ ] Support `show`/`hide` and stable ordering.
- [ ] Keep comments/custom text in pack templates.

## DART-009 — Adapter facade

- [ ] Compose policies behind the public language adapter protocol.
- [ ] Accept immutable typed effective rules.
- [ ] Expose capabilities and diagnostics.
- [ ] Keep instances session-safe and free from global caches.

## DART-010 — Conformance and package-specific tests

- [ ] Pass shared language conformance for declared capabilities.
- [ ] Add null-safety, records, generic functions, package URI, relative URI, prefix, show/hide, deferred, and export conflict tests.
- [ ] Prove no Flutter widgets, state management, folder layout, pubspec ownership, or build-runner policy lives in the adapter.

## DART-011 — Documentation and release

- [ ] Document complete rule schema/defaults/capabilities.
- [ ] Document project-path versus `package:` binding examples.
- [ ] Build wheel/sdist and validate compatibility.
- [ ] Publish independently from Dart and Flutter packs.

## Completion gate

- shared conformance passes;
- every rule field is typed/introspectable/tested;
- relative and package imports resolve from actual planned paths;
- nullability is preserved correctly;
- no Flutter/framework/ecosystem execution logic exists;
- output is deterministic and IR remains immutable.
