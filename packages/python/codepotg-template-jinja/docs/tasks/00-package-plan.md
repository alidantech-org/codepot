# Jinja template-engine implementation plan

This package implements a sandboxed Jinja template-engine adapter. It does not own source normalization, target-language semantics, file selection, output planning, writing, commands, or framework behavior.

## JINJA-001 — Package and plugin foundation

**Status:** planned

**Dependencies:** core template-engine port, plugin descriptors, version primitives

- [ ] Add isolated package metadata, src layout, typing marker, README, and tests.
- [ ] Register `jinja` factory in `codepotg.template_engines`.
- [ ] Declare recognized suffixes such as `.jinja`, `.jinja2`, and `.j2` with deterministic precedence.
- [ ] Declare plugin/core/IR/behavior versions and actual capabilities.
- [ ] Add architecture tests proving no source, target adapter, writer, CLI, command, or project-manifest ownership.

## JINJA-002 — Typed engine rule schema

**Status:** planned

Define immutable rules, override patches, descriptors, defaults, merge policy, hard restrictions, examples, and introspection for:

### Undefined behavior

- [ ] strict error default;
- [ ] optional debug/placeholder modes only when approved by the engine contract;
- [ ] source-spanned undefined diagnostics.

### Whitespace and encoding

- [ ] trim blocks;
- [ ] left-strip blocks;
- [ ] keep trailing newline;
- [ ] newline sequence;
- [ ] source/output encoding policy.

### Includes and inheritance

- [ ] declared include policy;
- [ ] dynamic include disabled by default;
- [ ] maximum include depth;
- [ ] target compatibility enforcement;
- [ ] cycle diagnostics.

### Sandbox and context access

- [ ] restricted attribute policy;
- [ ] registered-callable-only policy;
- [ ] deny Python imports/builtins/environment/filesystem/network/process access;
- [ ] host-only security fields that packs cannot enable.

### Helpers

- [ ] registered filters/tests/globals descriptors;
- [ ] conflict policy;
- [ ] helper behavior/version contribution to cache keys.

### Limits

- [ ] maximum rendered bytes;
- [ ] maximum include depth;
- [ ] optional iteration/context depth bounds where feasible;
- [ ] cancellation checkpoints.

### Named outputs

- [ ] capability and syntax policy for declared named output blocks;
- [ ] undeclared output rejection.

**Acceptance:** unknown engine fields are errors and pack/project overrides cannot enable host-forbidden behavior.

## JINJA-003 — Immutable render context adapter

- [ ] Accept only core-prepared immutable mappings/sequences/scalars and narrow registered helper objects.
- [ ] Prevent mutation of context and registries.
- [ ] Convert unsupported rich objects into diagnostics before rendering.
- [ ] Exclude filesystem, pack provider, runtime, writer, cache store, command executor, environment, and secret objects.

## JINJA-004 — Pack template loader

- [ ] Resolve templates by descriptor ID/path through the pack template registry.
- [ ] Enforce pack-root containment.
- [ ] Reject ignored, documentation-only, static, and binary files as template includes.
- [ ] Support partials and authored templates.
- [ ] Preserve source identity and line mappings.

## JINJA-005 — Include/inheritance planner integration

- [ ] Consume planner-declared include dependencies.
- [ ] Validate same-target or neutral fragment compatibility.
- [ ] Detect cycles and depth violations before render.
- [ ] Reject undeclared dynamic includes by default.
- [ ] Ensure include digests contribute to compiled cache identity.

## JINJA-006 — Safe environment construction

- [ ] Construct one immutable/configured environment per runtime cache scope or equivalent safe pool.
- [ ] Use sandboxed Jinja facilities plus explicit guards.
- [ ] Register only declared filters/tests/globals.
- [ ] Remove unsafe defaults and prove denial through adversarial tests.
- [ ] Avoid process-global environment mutation.

## JINJA-007 — Rendering and diagnostics

- [ ] Compile and render with cancellation checks and size limits.
- [ ] Convert syntax, undefined, include, helper, and runtime errors into typed diagnostics with source spans and include stack.
- [ ] Preserve deterministic text output.
- [ ] Never write files directly.

## JINJA-008 — Named output blocks

- [ ] Implement only after core declared-output contracts are stable.
- [ ] Map output block IDs to planner-declared outputs.
- [ ] Reject duplicate, missing, or undeclared blocks.
- [ ] Enforce per-output and total size limits.
- [ ] Keep output paths outside template control.

## JINJA-009 — Compiled-template cache

- [ ] Key by engine behavior version, typed rule digest, template source digest, include dependency digests, and helper/filter version digest.
- [ ] Keep cache session/runtime scoped through the cache port.
- [ ] Avoid mutable module-level caches.
- [ ] Test invalidation, corruption, and concurrent access.

## JINJA-010 — Conformance and security tests

- [ ] Pass shared engine conformance.
- [ ] Add sandbox escape attempts for attributes, callables, imports, builtins, filesystem, environment, network, and process access.
- [ ] Add undefined, whitespace, encoding, include, inheritance, cycle, limit, cancellation, cache, named output, and source-span tests.
- [ ] Prove contexts and registries remain unchanged after success/failure.

## JINJA-011 — Documentation and release

- [ ] Document complete engine rules and host-only restrictions.
- [ ] Document safe partial/include patterns and named outputs.
- [ ] Document helper registration for plugin authors.
- [ ] Build wheel/sdist and test independent installation.

## Completion gate

- shared engine conformance and adversarial sandbox tests pass;
- templates cannot access filesystem, environment, network, commands, Python imports, or rich runtime objects;
- includes resolve only through the pack registry and target compatibility;
- output paths are always planner-owned;
- cache identity contains all behavior-affecting inputs;
- no generation/business logic exists in this package.
