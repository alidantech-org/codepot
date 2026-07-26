# Path-expression and semantic naming tasks

This lane implements the approved rule that a pack source path is the default output-path program.

## Prohibited shortcuts

No task in this lane may:

- add `fileName`, `filePath`, `directory`, or similar generated-output properties to neutral IR records;
- evaluate Jinja, Python, JavaScript, or arbitrary methods while planning paths;
- let a template engine choose output destinations;
- silently stringify or join arbitrary sequences;
- use target-language adapters to select output folders;
- bypass planning for static or binary files;
- restore the old runtime or parse old `paths.yaml`.

## PATH-001 — Semantic name and inflection model

**Status:** planned

**Dependencies:** CORE-003, IR-001

**Ownership:** `codepotg-v2/domain/ir` or a focused core naming package approved by architecture.

- [ ] Implement immutable semantic name source value.
- [ ] Implement case projections: raw, clean, snake, kebab, camel, pascal, screaming, constant, dot, path, lower, upper.
- [ ] Implement original, singular, plural, and number projections with long and short aliases.
- [ ] Define deterministic word splitting, acronym handling, Unicode normalization, invalid-character behavior, and empty-name diagnostics.
- [ ] Implement behavior-versioned inflection with irregular and uncountable word support.
- [ ] Include naming/inflection behavior version in plan, lock, and cache identities.
- [ ] Add property tests proving case/plurality projections are immutable and deterministic.

**Acceptance:** `[entity.name.kebab.s]`, `[resource.name.path.o]`, and all documented projections resolve without target-language or filesystem dependencies.

## PATH-002 — Typed path-value registry

**Status:** planned

**Dependencies:** CFG-002, PATH-001, CORE-004

**Ownership:** core path contracts and configuration introspection.

- [ ] Define typed path-safe scalar, semantic-name projection, `PathSegments`, optional value, and registered namespaced value descriptors.
- [ ] Register stable roots for project, pack, source, unit, option, binding, group, artifact, target metadata, and active selection aliases.
- [ ] Require plugin-provided path values to be typed, namespaced, documented, deterministic, and capability-scoped.
- [ ] Expose registry metadata for diagnostics, editor completion, schema/help output, and `inspect paths`.
- [ ] Reject raw parser/source objects and unregistered mapping access.

**Acceptance:** every path property is discoverable through typed metadata and unknown roots/properties produce source-spanned suggestions.

## PATH-003 — Path token parser

**Status:** planned

**Dependencies:** PATH-002

**Ownership:** generation domain, not Jinja or language adapters.

- [ ] Parse literal segments.
- [ ] Parse `{recipe}` named path recipe tokens.
- [ ] Parse `[expression]` bounded dynamic tokens.
- [ ] Parse `[[value]]` and `{{value}}` literal escaping.
- [ ] Support dynamic scalar interpolation inside a filename segment.
- [ ] Allow multi-segment `PathSegments` only when the token occupies a complete source segment.
- [ ] Preserve token source spans for diagnostics.
- [ ] Reject method calls, arbitrary indexing, malformed nesting, and unsupported token combinations.

**Acceptance:** Next.js-style bracket routes, literal braces, and dynamic names compile without ambiguity.

## PATH-004 — Named path recipe contract

**Status:** planned

**Dependencies:** PACKCFG-001..PACKCFG-004, PLAN-002, PATH-003

**Ownership:** typed `CodepotgPack.yaml` model plus planner.

- [ ] Implement `paths` mapping in the pack manifest.
- [ ] Support structural recipes with parts only.
- [ ] Support selection-only recipes with zero output parts.
- [ ] Support selection-plus-parts recipes.
- [ ] Support references to named selections and inline selections.
- [ ] Evaluate recipe tokens left to right.
- [ ] Make aliases introduced by earlier recipes available to later recipes and expressions.
- [ ] Reject alias shadowing, missing prior aliases, recursive recipes, and selection cycles.
- [ ] Record recipe and selection provenance in the plan.

**Acceptance:** `{resource}/{entity}/[entity.name.kebab.s].entity.ts.jinja` can nest resource and entity fan-out deterministically.

## PATH-005 — Source-path output compiler

**Status:** planned

**Dependencies:** PLAN-001, PATH-003, PATH-004, target registry

**Ownership:** generation planner.

- [ ] Treat each content-root-relative source path as the default output expression.
- [ ] Establish exact-file selection before resolving dynamic tokens.
- [ ] Resolve named recipes and typed expressions.
- [ ] Preserve literal prefixes, suffixes, and target extensions.
- [ ] Strip only the registered template-engine suffix for emitted templates.
- [ ] Preserve static/binary source suffixes and bytes.
- [ ] Prepend the project pack-instance output root only after pack-relative path compilation.
- [ ] Produce immutable output-expression and resolved-path values.
- [ ] Ensure target adapters validate final filename restrictions but do not plan directories.

**Acceptance:** no normal template or static descriptor requires an explicit `output` field.

## PATH-006 — Exceptional output overrides and named outputs

**Status:** planned

**Dependencies:** PATH-005

- [ ] Support explicit `output.parts` using the same typed grammar.
- [ ] Support output overrides only when source layout cannot represent the destination cleanly.
- [ ] Support multiple named outputs only when every ID/path is declared before rendering.
- [ ] Prevent engines/templates from adding output IDs or destinations dynamically.
- [ ] Include override provenance in plan inspection.

**Acceptance:** exceptional overrides remain typed and cannot unlock arbitrary template expressions.

## PATH-007 — Path safety and collision validation

**Status:** planned

**Dependencies:** PATH-005, PATH-006

- [ ] Reject absolute paths, traversal, empty invalid segments, NUL/control characters, and output-root escapes.
- [ ] Validate platform-reserved names and target-specific final filename restrictions.
- [ ] Detect exact, normalized, and case-insensitive collisions where relevant.
- [ ] Validate path-length policy and symlink boundaries before writing.
- [ ] Detect duplicate destinations across template, barrel, static, binary, and named outputs before rendering.

**Acceptance:** an invalid destination prevents renderer and writer invocation.

## PATH-008 — Static/binary and folder fan-out conformance

**Status:** planned

**Dependencies:** PATH-005, PLAN-002

- [ ] Prove selection-bearing recipe tokens fan out template, static, and binary source files consistently.
- [ ] Preserve relative structure following recipe tokens.
- [ ] Prove static bytes remain unchanged.
- [ ] Test nested resource/module/package fan-out.
- [ ] Test `.gitignore`, `.env.example`, images, fixture files, and route folders.

**Acceptance:** static files receive the same path power as rendered templates without becoming templates.

## PATH-009 — Introspection and documentation tooling

**Status:** planned

**Dependencies:** PATH-002..PATH-008

- [ ] Implement structured `inspect paths` output showing source path, tokens, selections, aliases, resolved parts, target/engine suffix handling, and final destination.
- [ ] Expose available path roots and name projections for editor/LSP completion.
- [ ] Add diagnostics examples to public docs.
- [ ] Document behavior-version changes and lock/cache impact.

**Acceptance:** pack authors can understand exactly why a source file resolves to a destination without reading runtime internals.

## PATH-010 — Real pack fixtures

**Status:** planned

**Dependencies:** PATH-001..PATH-009

- [ ] Add a TypeScript fixture using case and singular/plural variants.
- [ ] Add a Dart package fixture using package/resource path recipes.
- [ ] Add a Next.js fixture with literal bracket route folders.
- [ ] Add nested resource/entity fan-out.
- [ ] Add a static/binary fan-out fixture.
- [ ] Add an aggregate single-file template.
- [ ] Add explicit output-override and multiple-output fixtures.
- [ ] Add negative fixtures for invented `fileName`, invalid properties, alias cycles, traversal, and collisions.

**Acceptance:** all official pack packages consume the same path conformance fixtures and no fixture depends on hidden filename convenience properties.
