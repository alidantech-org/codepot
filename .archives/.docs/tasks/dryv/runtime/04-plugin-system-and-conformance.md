# Plugin system and conformance tasks

Plugins provide bounded runtime capabilities. They cannot extend the closed Dryv semantic kernel or author generated source syntax outside templates.

## PLUG-001 — Public descriptors

- [x] Category, ID, aliases, distribution, version, API versions, compatibility, capabilities, trust, and factory metadata.
- [x] Immutable descriptor validation.
- [x] No semantic-node, facet, selector, expression-root, or context-extension capability.
- [ ] Publish stable descriptor introspection through `DryvRuntime`.

## PLUG-002 — Entry-point discovery

- [x] Standard `importlib.metadata.entry_points` discovery.
- [x] Lazy factory loading.
- [x] Runtime-owned plugin instances.
- [x] Duplicate IDs and aliases fail safely.
- [x] Package import itself performs no discovery.
- [ ] Expose structured discovery diagnostics without hiding unrelated healthy plugins.

## PLUG-003 — Runtime validation and inspection

- [ ] Add `runtime.validate_plugin(...)`.
- [ ] Add `runtime.plugins()` and `runtime.inspect_plugin(...)`.
- [ ] Validate distribution metadata, API ranges, aliases, capabilities, protocols, and factory results.
- [ ] Return serializable diagnostics suitable for CLI, IDE, server, and MCP hosts.

## PLUG-004 — Least-authority contexts

- [x] Target plugins receive only target/path requests, options, diagnostics, and immutable planning facts.
- [x] Template engines receive only template text, immutable prepared context, declared partials, diagnostics, and cancellation.
- [x] Contract loaders receive only controlled source data and public IR operations.
- [ ] Define equally narrow contexts before adding pack providers, ecosystems, caches, writers, or executors as plugins.
- [ ] Expand session-isolation and no-retained-context tests.

## PLUG-005 — Contract-provider conformance

- [x] Built-in canonical IR loader returns deterministic validated contracts.
- [x] No provider-specific type escapes into plans or contexts.
- [x] Cancellation, bounded input, strict decoding, and stable digest coverage.
- [ ] Add conformance helpers for Python callable and host-supplied contract providers.
- [ ] Prove repeated provider calls do not leak mutable session state.

## PLUG-006 — Target-plugin conformance

- [x] Target descriptors and longest-known suffix inference.
- [x] Filename, identifier, reserved-name, and output-path validation.
- [x] Relative, package, alias, and explicit module/path facts.
- [x] Typed immutable options and exact diagnostics.
- [x] No rendered types, literals, comments, imports, exports, validators, decorators, formatting, or framework snippets.
- [ ] Add capability-aware conformance so plugins are not forced to claim unsupported features.

## PLUG-007 — Template-engine conformance

- [x] Deterministic rendering and strict undefined behavior.
- [x] Immutable bounded contexts and declared partials.
- [x] Cancellation, output limits, syntax diagnostics, and sandbox denial tests.
- [x] No filesystem, environment, network, Python import, arbitrary callable, command, or destination access.
- [ ] Publish cache identity contracts only after the runtime cache port is approved.

## PLUG-008 — Pack-provider conformance

- [ ] Immutable resolution identity.
- [ ] Local/Git containment and subdirectory safety.
- [ ] Content and manifest digests.
- [ ] Cancellation and partial-snapshot cleanup.
- [ ] Credential redaction.
- [ ] Providers supply snapshots only; typed runtime loaders decode manifests and templates.

## PLUG-009 — Ecosystem conformance

- [ ] Known manifest detection and typed contributions.
- [ ] Conflict handling and owned/contributed modes.
- [ ] Toolchain capability resolution without silent switching.
- [ ] Action planning without direct execution.
- [ ] No semantic-kernel or generated-syntax ownership.

## PLUG-010 — Infrastructure conformance

Writer:

- staging, comparison, lifecycle reporting, rollback, path safety, and ownership state.

Cache:

- complete behavior keys, isolation, corruption handling, bounds, and deterministic reuse.

Executor:

- exact arguments, timeout, cancellation, environment filtering, capability enforcement, output capture, and process-tree cleanup.

Generated-output hashes remain outside `dryv.lock.yaml`.

## Acceptance gate

- Discovery uses no internal directory scanning or decorator side effects.
- Registries and plugin instances belong to runtime sessions.
- Official packages pass the same public suites available to third parties.
- Plugins cannot extend semantic objects, relations, facets, selectors, expressions, contexts, or validators.
- Target plugins cannot author generated source syntax.
- Every descriptor, compatibility, loading, and configuration conflict has a stable diagnostic.
