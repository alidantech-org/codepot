# Jinja template-engine implementation plan

This package implements a sandboxed Jinja template-engine adapter. It does not own source normalization, target-language semantics, file selection, output planning, writing, commands, or framework behavior.

Status values distinguish implemented current-port behavior from integrations blocked by public core contracts. A task marked implemented is not the same as a released package. JINJA-011 is now release-verified for the current public port; blocked integrations remain separate future work.

## JINJA-001 — Package and plugin foundation

**Status:** implemented in PR #28

**Dependencies:** core template-engine port, plugin descriptors, version primitives

- [x] Add isolated package metadata, src layout, typing marker, README, and tests.
- [x] Register `jinja` factory in `codepotg.template_engines`.
- [x] Declare `.j2`, `.jinja`, and `.jinja2` with deterministic ordering.
- [x] Declare plugin/core/IR/behavior versions and actual capabilities.
- [x] Add architecture tests proving no source, target adapter, writer, CLI, command, or project-manifest ownership.

## JINJA-002 — Typed engine rule schema

**Status:** implemented for the current public render port; project/pack rule decoding and named outputs remain blocked

- [x] Strict undefined behavior.
- [x] Typed whitespace and newline behavior.
- [x] Static declared dependency policy and maximum include depth.
- [x] Restricted attribute and callable policy.
- [x] Denial of Python imports, builtins, environment, filesystem, network, and process access.
- [x] Registered helper descriptors, conflict policy, and cache identity contribution.
- [x] Template, partial, context, AST, output, and cache limits.
- [x] Cooperative cancellation checkpoints.
- [ ] Decode rules from project/pack configuration after a public configuration bridge exists.
- [ ] Enforce target-compatible partial roles after planner/template-registry metadata exists.

Named-output rules belong only to JINJA-008.

## JINJA-003 — Immutable render context adapter

**Status:** implemented in PR #28

- [x] Accept safe scalars, tuples, sorted tuple-pair mappings, public frozen CodepotG IR values, approved enums, and narrow helper descriptors.
- [x] Prevent mutation of caller context and helper registries.
- [x] Convert unsupported rich objects into structured diagnostics before rendering.
- [x] Exclude filesystem, pack provider, runtime, writer, cache store, command executor, environment, and secret objects.

## JINJA-004 — Request-owned template registry and loader

**Status:** implemented for the current public port; full pack-registry integration blocked

- [x] Resolve the root and declared partials from one immutable request-owned registry.
- [x] Reject traversal, absolute, Windows-ambiguous, duplicate, colliding, oversized, and unsorted identifiers.
- [x] Support authored root templates and declared partials without filesystem fallback.
- [x] Preserve template IDs as diagnostic source identities.
- [ ] Consume a public pack template registry when core publishes that contract.
- [ ] Enforce pack-root ignore/static/binary roles when planner/template-registry metadata exists.

## JINJA-005 — Static dependency analysis

**Status:** implemented for request partials; planner-declared and target-compatible integration blocked

- [x] Analyze static include, extends, import, and from-import dependencies before render.
- [x] Detect missing dependencies, dynamic dependencies, cycles, and excessive depth.
- [x] Reject `ignore missing` and dependency lists.
- [x] Include all reachable dependency digests in compilation identity.
- [ ] Consume planner-declared include metadata after the public planner contract exists.
- [ ] Validate same-target or neutral-fragment compatibility after target-role metadata exists.

## JINJA-006 — Safe environment construction

**Status:** implemented in PR #28; callable compatibility decision completed by the audit-fix lane

- [x] Use `SandboxedEnvironment` plus explicit attribute/callable guards.
- [x] Use `StrictUndefined`.
- [x] Clear default filters, tests, and globals.
- [x] Register only approved helpers.
- [x] Avoid process-global environment mutation.
- [x] Prove denial through adversarial tests.
- [x] Keep `loop.cycle()` and `loop.changed()` deliberately denied and cover the exact behavior with compatibility tests.

## JINJA-007 — Rendering and diagnostics

**Status:** implemented in PR #28; root-source diagnostic correction completed by the audit-fix lane

- [x] Compile and render with cancellation checks and byte limits.
- [x] Stream chunks instead of creating an unbounded complete string first.
- [x] Convert syntax, undefined, include, helper, sandbox, limit, cancellation, and runtime failures into typed diagnostics.
- [x] Preserve deterministic text output.
- [x] Return no partial content on failure.
- [x] Never write files directly.
- [x] Report malformed root source values as `JINJA_TEMPLATE_INVALID`; keep partial-source failures under `JINJA_PARTIAL_INVALID`.

## JINJA-008 — Named output blocks

**Status:** blocked on a public planner-declared named-output request/result contract

- [ ] Define named-output capability and syntax only after the core contract exists.
- [ ] Map output IDs only to planner-declared outputs.
- [ ] Reject duplicate, missing, and undeclared output blocks.
- [ ] Enforce per-output and total limits.
- [ ] Keep paths outside template control.

No author-private result type or encoded multi-file string is permitted.

## JINJA-009 — Compiled-template cache

**Status:** implemented as a bounded engine-instance cache; runtime cache-port integration blocked

- [x] Key by engine/package behavior, typed rules, Jinja version, root source, reachable partial digests, and helper versions.
- [x] Keep cache engine-instance-owned, bounded, locked, and clearable.
- [x] Avoid mutable module-level caches.
- [x] Test hits, invalidation, eviction, and concurrent access.
- [ ] Integrate with a runtime cache port after a suitable compiled-object cache contract is public.

## JINJA-010 — Conformance and security tests

**Status:** implemented in PR #28; audit compatibility and diagnostic cases added

- [x] Pass shared engine conformance against the verified public core package.
- [x] Add sandbox attempts for attributes, callables, imports, builtins, filesystem, environment, network, and process access.
- [x] Add undefined, whitespace, encoding, include, inheritance, cycle, limit, cancellation, cache, and source-aware diagnostic tests.
- [x] Prove contexts and registries remain unchanged after success/failure.
- [x] Add exact compatibility tests for denied `loop.cycle()` and `loop.changed()` calls.
- [x] Add a malformed-root-source diagnostic regression test.
- [ ] Add named-output tests only after JINJA-008 is unblocked.

## JINJA-011 — Documentation and release

**Status:** release_verified_current_port

- [x] Document current engine rules and host-only restrictions.
- [x] Document safe request-partial/include behavior.
- [x] Document blocked named outputs and missing integrations.
- [x] Document helper registration.
- [x] Document the deliberate denial of `loop.cycle()` and `loop.changed()`.
- [x] Document root versus partial source diagnostic ownership.
- [x] Run Ruff check and formatting against exact current-branch package sources.
- [x] Run the complete real `codepotg-v2` suite and build.
- [x] Re-run the complete Jinja suite against the verified real core package.
- [x] Build core and Jinja wheels and source distributions.
- [x] Install the real core and Jinja wheels together in a fresh environment.
- [x] Repeat entry-point, simple-render, static-partial, and denied-loop-callable checks.
- [x] Record exact synchronized release evidence and close the PR #28 audit fixes.

Verification totals and artifact hashes are recorded in [`PROGRESS.md`](PROGRESS.md).

## Audit follow-up

See:

- [`../audits/2026-07-27-pr-28-audit.md`](../audits/2026-07-27-pr-28-audit.md)
- [`AUDIT_FIXES.md`](AUDIT_FIXES.md)

## Completion gate

The current public-port package is complete because:

- shared engine conformance and adversarial sandbox tests pass against the verified real core package;
- templates cannot access filesystem, environment, network, commands, Python imports, or rich runtime objects;
- current-port dependencies resolve only from the request-owned registry;
- blocked pack/planner/named-output/cache-port integrations remain explicit rather than emulated;
- output paths remain planner-owned;
- cache identity contains all behavior-affecting implemented inputs;
- no generation/business logic exists in this package;
- Ruff, format, full tests, build, real-wheel install, and scoped clean-branch checks pass and are recorded.

JINJA-008, pack-registry integration, target-compatible partial metadata, project/pack rule decoding, and runtime cache-port integration remain blocked until public contracts exist. They do not prevent release of the current adapter port.
