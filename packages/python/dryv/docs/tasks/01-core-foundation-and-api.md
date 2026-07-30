# Core foundation and Python API tasks

## CORE-001 — Package metadata and isolated installation

**Status:** planned

**Owner:** `packages/python/dryv`

**Dependencies:** DOC-001..DOC-007

**Files:** `pyproject.toml`, package README, build/package metadata, `src/dryv/__init__.py`, `src/dryv/py.typed`, test configuration.

- [ ] Choose supported Python versions and document them.
- [ ] Configure src-layout packaging and typed package marker.
- [ ] Define core runtime dependencies separately from development/test dependencies.
- [ ] Ensure no dependency on the old `packages/python/dryv` distribution or source tree.
- [ ] Add an isolated wheel/sdist build test.
- [ ] Add a clean-environment import test.

**Prohibited shortcuts:** adding repository root to `sys.path`; importing old modules; relying on editable monorepo path behavior as packaging proof.

**Acceptance:** wheel installs in a fresh environment and `import dryv` exposes only intended public version/facade placeholders.

## CORE-002 — Public/private namespace policy

**Status:** planned

**Dependencies:** CORE-001

- [ ] Define supported exports from `dryv`, `dryv.api`, `dryv.config`, `dryv.ir`, `dryv.generation`, `dryv.plugins`, `dryv.ports`, `dryv.diagnostics`, and `dryv.testing`.
- [ ] Mark implementation-only modules private, including typed semantic graph indexes/builders.
- [ ] Add tests preventing adapter packages from importing private modules.
- [ ] Document public API compatibility expectations.
- [ ] Do not expose generic semantic node/edge/fact extension APIs.

**Acceptance:** all official adapters express their approved contracts using only public modules and none can extend the semantic kernel.

## CORE-003 — Version primitives

**Status:** planned

**Dependencies:** CORE-001

- [ ] Implement package, core API, plugin API, IR, schema, pack, naming behavior, selection behavior, planning behavior, and other behavior-version value objects.
- [ ] Keep these versions distinct.
- [ ] Implement constraint parsing or a narrow dependency on a proven version library.
- [ ] Add compatibility result objects and diagnostics.
- [ ] Test compatible, incompatible, prerelease, and malformed values.

**Acceptance:** plugin, pack, kernel, selector, and planner compatibility can be evaluated without scattered string comparisons.

## CORE-004 — Diagnostics and source spans

**Status:** planned

**Dependencies:** CORE-001

- [ ] Implement stable diagnostic code, severity, message, source span, related span, details, suggestion, and documentation reference.
- [ ] Implement source identity for files, memory inputs, Git packs, semantic objects, planned/generated artifacts, and templates.
- [ ] Add immutable diagnostic collections and deterministic ordering.
- [ ] Add diagnostic serialization for CLI/MCP/HTTP.
- [ ] Add package/subsystem code conventions.
- [ ] Preserve semantic and artifact relationships needed by explain/impact output.

**Tests:** focused construction, ordering, serialization, related locations, no mutable internals.

**Acceptance:** configuration, semantic, planning, and adapter packages report precise structured errors without generic exceptions for expected failures.

## CORE-005 — Events, cancellation, and operation results

**Status:** planned

**Dependencies:** CORE-004

- [ ] Implement operation/session IDs.
- [ ] Implement cancellation token and cancellation reason.
- [ ] Implement runtime event base and stable event types distinct from application-domain `group.events` semantics.
- [ ] Implement sync and async event sinks.
- [ ] Implement result status, diagnostics, readiness actions, timing, reproducibility metadata, and optional impact summary.
- [ ] Ensure event observer failure policy is explicit.
- [ ] Test cancellation at phase boundaries.

**Acceptance:** no core service prints progress or calls `sys.exit`; all frontends consume the same structured results/events without confusing runtime progress events with semantic application events.

## CORE-006 — Architecture tests

**Status:** planned

**Dependencies:** CORE-001..CORE-005

- [ ] Assert domain does not import application/infrastructure/runtime/CLI.
- [ ] Assert application does not import concrete infrastructure.
- [ ] Assert CLI is not imported below CLI.
- [ ] Assert no import from old `packages/python/dryv` paths.
- [ ] Assert no mutable global plugin/config registry.
- [ ] Assert no same-name module/package collision in the new tree.
- [ ] Assert package import does not perform plugin discovery, filesystem access, or process mutation.
- [ ] Assert only core owns semantic objects, facets, selectors, expression roots, template-context contracts, and semantic validation.
- [ ] Assert target adapters contain no source-code renderer ports.
- [ ] Assert templates/static files are the only emitted-text sources.

**Acceptance:** architecture suite fails on representative forbidden imports, semantic extension, and syntax-rendering paths.

## API-001 — Runtime composition and facade

**Status:** planned

**Dependencies:** CORE-003..CORE-006, PLUG-001..PLUG-004

- [ ] Define immutable `Dryv` facade.
- [ ] Implement `standard()` composition using installed defaults.
- [ ] Implement explicit composition for hosts and tests.
- [ ] Create isolated operation sessions.
- [ ] Ensure reusable runtime is safe for concurrent independent sessions.
- [ ] Compose the closed-kernel, validator, selector, planner, impact, engine, target, provider, writer, cache, and executor services explicitly.

**Acceptance:** test runtimes substitute every infrastructure port without monkey patching or semantic-kernel replacement.

## API-002 — Typed operations

**Status:** planned

**Dependencies:** API-001 plus owning use-case tasks

- [ ] Define requests/results for configure, validate, inspect, plan, impact/blast-radius, generate, plugin inspection, pack resolution, approvals, cache, generation state, and lock operations.
- [ ] Provide sync and async variants without duplicating business logic.
- [ ] Support filesystem, memory, and archive output requests.
- [ ] Support in-memory source and pack fixtures.
- [ ] Add stable structured serialization.
- [ ] Ensure inspect/impact use the same semantic/artifact plan as generation.

**Acceptance:** CLI and an MCP-style test adapter invoke only these operations and return equivalent plans/impact data.

## API-003 — Server-safe operation

**Status:** planned

**Dependencies:** API-001, CMD-001

- [ ] Implement server-safe host policy preset.
- [ ] Deny commands, secrets, environment inheritance, and uncontrolled filesystem/network access.
- [ ] Support cancellation/deadlines and bounded event streaming.
- [ ] Test concurrent sessions for state leakage.
- [ ] Ensure source adapters cannot request unauthorized reference loading and templates cannot access host services.

**Acceptance:** a server can validate, inspect, plan impact, and generate to memory with no writable project directory or command capability.
