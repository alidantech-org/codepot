# Selection-folder, path-expression, and naming tasks

This lane implements the approved filesystem-driven, root-first, closed-kernel path model.

## PATH-001 — Semantic names

**Status:** planned

**Dependencies:** CORE-003, IR-001

- [ ] Implement immutable names with raw, clean, snake, kebab, camel, pascal, screaming, constant, dot, path, lower, and upper forms.
- [ ] Implement original, singular, plural, and number projections with short and long names.
- [ ] Enforce the one public ordering `x.name.{casing}.{number}`.
- [ ] Make inflection deterministic and behavior-versioned.
- [ ] Add irregular, uncountable, acronym, Unicode, and empty-name tests.

**Acceptance:** `(mapping.schema.name.kebab.s)`, `(operation.name.camel.original)`, and every documented name form resolve deterministically; reversed casing/number order is rejected.

## PATH-002 — Closed typed expression registry

**Status:** planned

**Dependencies:** CFG-002, PATH-001, CORE-004, closed kernel

- [ ] Define typed scalar, name, path-segment, optional, and namespaced descriptors.
- [ ] Register only documented semantic contexts plus project, pack, source, option, binding, imports, exports, artifact, and target metadata.
- [ ] Include known roots such as group, schema, field, operation, input, output, failure, view, mapping, workflow, step, policy, and event.
- [ ] Preserve outer-to-inner property order such as `mapping.schema` and `step.compensation.operation`.
- [ ] Expose descriptors for diagnostics, completion, schemas, and inspection.
- [ ] Reject unknown roots/properties with suggestions.
- [ ] Prevent adapters/packs from registering semantic roots or properties.
- [ ] Reject resource, model, entity, frontend, UI, language class-name, fileName, filePath, and directory roots/properties.

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
- [ ] Establish fixed root-first selector contexts before later expressions.
- [ ] Evaluate nested selection folders left to right.
- [ ] Support optional inline aliases and reject shadowing/cycles.
- [ ] Reject reversed or invalid active-parent scopes.

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
- [ ] Treat `.gitignore` as control and `.gitignore.jinja` as emitting.
- [ ] Prepend the pack-instance output root after pack-relative compilation.

**Acceptance:** ordinary files need no manifest `files`, `filePatterns`, profiles, roles, or output override.

## PATH-006 — Root-first fixed selector registry

**Status:** planned

**Dependencies:** PATH-004, IR selector contracts

- [ ] Implement versioned preferred selectors beginning with `groups`.
- [ ] Implement active-parent selectors beginning with `group` inside nested scope.
- [ ] Cover schemas, object/enum/DTO schema views, operations, operation inputs/outputs/failures, views, storage mappings, workflows, policies, and events.
- [ ] Implement `.each` and `.all`.
- [ ] Infer stable singular/plural contexts.
- [ ] Implement optional `selector(alias)` without shadowing.
- [ ] Support documented project-wide selectors only for genuine global reports/indexes and expose discouragement metadata.
- [ ] Expose the registry through schema/editor/inspection APIs.
- [ ] Reject resource/entity/model/frontend/UI, reversed-root, arbitrary `where/traverse/depth`, and pack-defined `from/as` traversal.
- [ ] Prevent plugins from registering selectors.

## PATH-007 — Safety and collisions

**Status:** planned

**Dependencies:** PATH-005, PATH-006

- [ ] Reject absolute paths, traversal, root escapes, invalid segments, and platform-reserved names.
- [ ] Detect exact, normalized, and case-insensitive collisions where relevant.
- [ ] Validate path length and target filename restrictions.
- [ ] Detect all duplicate destinations before rendering.
- [ ] Preserve target adapter responsibility as validation only; adapters cannot choose directories or render syntax.

## PATH-008 — Planned dependency/export path facts

**Status:** planned

**Dependencies:** PATH-005, BIND-002, planning graph

- [ ] Attach selection key, semantic identity/scope, artifact identity, destination, and declared symbols to each planned emission.
- [ ] Resolve imports only from declared selection keys and semantic provider matches.
- [ ] Resolve ordered exports including barrels exporting barrels.
- [ ] Preserve project-wide, `.all`, `.each`, and active-parent scope.
- [ ] Calculate destination-relative facts and request target-aware module/path validation.
- [ ] Supply immutable descriptors to templates.
- [ ] Prohibit pre-rendered import/export statements from target adapters.
- [ ] Reject dependency cycles, ambiguity, missing providers, and symbol conflicts before rendering.

## PATH-009 — Inspection and editor support

**Status:** planned

**Dependencies:** PATH-001..PATH-008

- [ ] Show source path, selection folders, contexts, expressions, resolved segments, suffix handling, and final destination.
- [ ] Show semantic/provider/import/export graphs.
- [ ] Expose available expressions, fixed selectors, aliases, and selection keys for completion.
- [ ] Explain removed roots/selectors and suggest closed-kernel replacements.
- [ ] Document naming/selection behavior-version effects on locks, cache, and generation state.

## PATH-010 — Conformance fixtures

**Status:** planned

**Dependencies:** PATH-001..PATH-009

- [ ] Use checked-in TypeORM, TypeScript SDK, and Flutter integration manifests as fixtures.
- [ ] Add matching template trees and expected outputs.
- [ ] Add local, Git-root, and Git-monorepo project examples.
- [ ] Cover `{root}`, nested group selections, static/binary files, partials, ignore rules, and generated `.gitignore`.
- [ ] Cover bracket routes and escaped parenthesis routes.
- [ ] Cover semantic imports, authored barrels, symbols, missing providers, cycles, traversal, and collisions.
- [ ] Cover rejection of old vocabulary, reversed selectors, query DSLs, syntax-rendering adapters, and semantic filename conveniences.

**Acceptance:** official packs share one conformance matrix, use the naming order and root-first selector contract, and contain no root `paths`, explicit `files`, profiles, or semantic output-filename conveniences.
