# Core foundation and Python API tasks

## CORE-001 — Package metadata and isolated installation

**Status:** planned

**Owner:** `packages/python/codepotg-v2`

**Dependencies:** DOC-001..DOC-006

**Files:** `pyproject.toml`, package README, build/package metadata, `src/codepotg/__init__.py`, `src/codepotg/py.typed`, test configuration.

- [ ] Choose supported Python versions and document them.
- [ ] Configure src-layout packaging and typed package marker.
- [ ] Define core runtime dependencies separately from development/test dependencies.
- [ ] Ensure no dependency on the old `packages/python/codepotg` distribution or source tree.
- [ ] Add an isolated wheel/sdist build test.
- [ ] Add a clean-environment import test.

**Prohibited shortcuts:** adding repository root to `sys.path`; importing old modules; relying on editable monorepo path behavior as packaging proof.

**Acceptance:** wheel installs in a fresh environment and `import codepotg` exposes only intended public version/facade placeholders.

## CORE-002 — Public/private namespace policy

**Status:** planned

**Dependencies:** CORE-001

- [ ] Define supported exports from `codepotg`, `codepotg.api`, `codepotg.config`, `codepotg.ir`, `codepotg.generation`, `codepotg.plugins`, `codepotg.ports`, `codepotg.diagnostics`, and `codepotg.testing`.
- [ ] Mark implementation-only modules private.
- [ ] Add tests preventing plugin packages from importing private modules.
- [ ] Document public API compatibility expectations.

**Acceptance:** all official adapters can express their contracts using only public modules.

## CORE-003 — Version primitives

**Status:** planned

**Dependencies:** CORE-001

- [ ] Implement package, core API, plugin API, IR, schema, pack, and behavior-version value objects.
- [ ] Keep these versions distinct.
- [ ] Implement constraint parsing or a narrow dependency on a proven version library.
- [ ] Add compatibility result objects and diagnostics.
- [ ] Test compatible, incompatible, prerelease, and malformed values.

**Acceptance:** plugin and pack compatibility can be evaluated without string comparisons scattered through the runtime.

## CORE-004 — Diagnostics and source spans

**Status:** planned

**Dependencies:** CORE-001

- [ ] Implement stable diagnostic code, severity, message, source span, related span, details, suggestion, and documentation reference.
- [ ] Implement source identity for files, memory inputs, Git packs, and generated artifacts.
- [ ] Add immutable diagnostic collections and deterministic ordering.
- [ ] Add diagnostic serialization for CLI/MCP/HTTP.
- [ ] Add package/subsystem code conventions.

**Tests:** focused construction, ordering, serialization, related locations, no mutable internals.

**Acceptance:** configuration and plugin packages can report precise structured errors without raising generic `ValueError` for expected failures.

## CORE-005 — Events, cancellation, and operation results

**Status:** planned

**Dependencies:** CORE-004

- [ ] Implement operation/session IDs.
- [ ] Implement cancellation token and cancellation reason.
- [ ] Implement event base and stable event types.
- [ ] Implement sync and async event sinks.
- [ ] Implement result status, diagnostics, readiness actions, timing, and reproducibility metadata.
- [ ] Ensure event observer failure policy is explicit.
- [ ] Test cancellation at phase boundaries.

**Acceptance:** no core service prints progress or calls `sys.exit`; all frontends can consume the same structured result/events.

## CORE-006 — Architecture tests

**Status:** planned

**Dependencies:** CORE-001..CORE-005

- [ ] Assert domain does not import application/infrastructure/runtime/CLI.
- [ ] Assert application does not import concrete infrastructure.
- [ ] Assert CLI is not imported below CLI.
- [ ] Assert no import from old `packages/python/codepotg` paths.
- [ ] Assert no mutable global plugin/config registry.
- [ ] Assert no same-name module/package collision in the new tree.
- [ ] Assert package import does not perform plugin discovery, filesystem access, or process mutation.

**Acceptance:** architecture suite fails on representative forbidden imports.

## API-001 — Runtime composition and facade

**Status:** planned

**Dependencies:** CORE-003..CORE-005, PLUG-001..PLUG-004

- [ ] Define immutable `CodepotG` facade.
- [ ] Implement `standard()` composition using installed defaults.
- [ ] Implement explicit composition for hosts and tests.
- [ ] Create isolated operation sessions.
- [ ] Ensure reusable runtime is safe for concurrent independent sessions.

**Acceptance:** test runtimes can substitute every infrastructure port without monkey patching.

## API-002 — Typed operations

**Status:** planned

**Dependencies:** API-001 plus owning use-case tasks

- [ ] Define requests/results for configure, validate, inspect, plan, generate, plugin inspection, pack resolution, approvals, cache, and lock operations.
- [ ] Provide sync and async variants without duplicating business logic.
- [ ] Support filesystem, memory, and archive output requests.
- [ ] Support in-memory source and pack fixtures.
- [ ] Add stable structured serialization.

**Acceptance:** CLI and an MCP-style test adapter invoke only these operations.

## API-003 — Server-safe operation

**Status:** planned

**Dependencies:** API-001, CMD-001

- [ ] Implement server-safe host policy preset.
- [ ] Deny commands, secrets, environment inheritance, and uncontrolled filesystem/network access.
- [ ] Support cancellation/deadlines and bounded event streaming.
- [ ] Test concurrent sessions for state leakage.

**Acceptance:** a server can generate to memory with no writable project directory and no command capability.
