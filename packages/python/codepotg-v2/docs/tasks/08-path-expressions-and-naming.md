# Selection-folder, path-expression, and naming tasks

This lane implements the approved filesystem-driven path model.

## PATH-001 — Semantic names

**Status:** planned

**Dependencies:** CORE-003, IR-001

- [ ] Implement immutable names with raw, clean, snake, kebab, camel, pascal, screaming, constant, dot, path, lower, and upper forms.
- [ ] Implement original, singular, plural, and number projections with short and long names.
- [ ] Make inflection deterministic and behavior-versioned.
- [ ] Add irregular, uncountable, acronym, Unicode, and empty-name tests.

**Acceptance:** `(entity.name.kebab.s)` and every documented name form resolve deterministically.

## PATH-002 — Typed expression registry

**Status:** planned

**Dependencies:** CFG-002, PATH-001, CORE-004

- [ ] Define typed scalar, name, path-segment, optional, and namespaced descriptors.
- [ ] Register fixed-selection contexts plus project, pack, source, option, binding, artifact, and target metadata.
- [ ] Expose descriptors for diagnostics, completion, schemas, and inspection.
- [ ] Reject unknown roots and properties with suggestions.

## PATH-003 — Parenthesis expression parser

**Status:** planned

**Dependencies:** PATH-002

- [ ] Parse `(expression)` dynamic tokens.
- [ ] Parse `((value))` as literal `(value)` before dynamic parsing.
- [ ] Leave square brackets literal for framework routes.
- [ ] Support scalar interpolation inside filenames.
- [ ] Allow multi-segment path values only as whole path segments.
- [ ] Preserve token source spans.

**Acceptance:** `[id]`, `[...slug]`, `[[...slug]]`, and `((admin))` compile without ambiguity.

## PATH-004 — Selection folders

**Status:** planned

**Dependencies:** PACKCFG-004, PLAN selection contracts, PATH-003

- [ ] Parse only whole `{selectionKey}` folder segments.
- [ ] Resolve keys through pack `selections`.
- [ ] Implement built-in `{root}` with zero path contribution.
- [ ] Replace selection folders with compact `paths` arrays.
- [ ] Establish fixed selector contexts before later expressions.
- [ ] Evaluate nested selection folders left to right.
- [ ] Support optional inline aliases and reject shadowing/cycles.

## PATH-005 — Filesystem output compiler

**Status:** planned

**Dependencies:** PACKCFG-002, PATH-003, PATH-004, target/engine registries

- [ ] Treat each `templates/`-relative path as the default output expression.
- [ ] Apply pack `.gitignore`, `include`, and `exclude` discovery rules.
- [ ] Exclude `_partials/**` from emission.
- [ ] Resolve selection folders and path expressions.
- [ ] Preserve literal folders, suffixes, bracket routes, and target extensions.
- [ ] Strip only the recognized engine suffix.
- [ ] Copy static and binary files unchanged.
- [ ] Treat `.gitignore` as control and `.gitignore.jinja` as an emitting template.
- [ ] Prepend the pack-instance output root after pack-relative compilation.

**Acceptance:** ordinary files need no manifest `files`, `filePatterns`, roles, or output override.

## PATH-006 — Fixed selector registry

**Status:** planned

**Dependencies:** PATH-004, IR selector contracts

- [ ] Implement versioned selectors for resources, entities, schemas, models, DTOs, enums, operations, and documented nested contexts.
- [ ] Implement `.each` and `.all`.
- [ ] Infer stable singular/plural contexts.
- [ ] Implement optional `selector(alias)`.
- [ ] Expose the registry through schema/editor/inspection APIs.
- [ ] Reject pack-defined `from`/`as` traversal.

## PATH-007 — Safety and collisions

**Status:** planned

**Dependencies:** PATH-005, PATH-006

- [ ] Reject absolute paths, traversal, root escapes, invalid segments, and platform-reserved names.
- [ ] Detect exact, normalized, and case-insensitive collisions where relevant.
- [ ] Validate path length and target filename restrictions.
- [ ] Detect all duplicate destinations before rendering.

## PATH-008 — Planned import/export paths

**Status:** planned

**Dependencies:** PATH-005, BIND-002, planning graph

- [ ] Attach selection key, scope, resolved path, and declared symbols to each planned emission.
- [ ] Resolve imports only from declared selection keys.
- [ ] Resolve ordered exports including barrels exporting barrels.
- [ ] Preserve global, `.all`, `.each`, and parent scope.
- [ ] Supply immutable descriptors to language adapters and templates.
- [ ] Reject dependency cycles and symbol conflicts before rendering.

## PATH-009 — Inspection and editor support

**Status:** planned

**Dependencies:** PATH-001..PATH-008

- [ ] Show source path, selection folders, contexts, expressions, resolved segments, suffix handling, and final destination.
- [ ] Show selector/import/export graphs.
- [ ] Expose available expressions, fixed selectors, aliases, and selection keys for completion.
- [ ] Document behavior-version effects on locks and cache.

## PATH-010 — Conformance fixtures

**Status:** planned

**Dependencies:** PATH-001..PATH-009

- [ ] Use the checked-in TypeORM, TypeScript SDK, and Flutter SDK manifests as fixtures.
- [ ] Add matching template trees and expected outputs.
- [ ] Add local, Git-root, and Git-monorepo project examples.
- [ ] Cover `{root}`, nested selections, static/binary files, partials, ignore rules, and generated `.gitignore`.
- [ ] Cover bracket routes and escaped parenthesis routes.
- [ ] Cover imports, barrels, symbols, missing providers, cycles, traversal, and collisions.

**Acceptance:** official packs share one conformance matrix and use no root `paths`, explicit `files`, or semantic filename conveniences.
