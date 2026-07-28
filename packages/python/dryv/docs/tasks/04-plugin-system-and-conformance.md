# Adapter/plugin system and conformance tasks

Plugins extend supported source formats, target validation/path behavior, engines, providers, ecosystems, writers, caches, and executors. They cannot extend the closed semantic kernel or author generated source syntax.

## PLUG-001 — Public adapter descriptors

**Status:** planned

**Dependencies:** CORE-002..CORE-005

- [ ] Define category, ID, aliases, distribution, version, API version, core/IR constraints, capabilities, configuration ownership, documentation, trust, and factory.
- [ ] Define category-specific descriptor extensions without private core imports.
- [ ] Explicitly exclude semantic node/facet/selector/expression ownership from every plugin descriptor.
- [ ] Validate descriptor immutability and serialization.

## PLUG-002 — Entry-point discovery

**Status:** planned

**Dependencies:** PLUG-001

- [ ] Discover each category through `importlib.metadata.entry_points`.
- [ ] Load descriptor factories lazily.
- [ ] Report broken distributions/entry points as diagnostics while keeping unrelated adapters available.
- [ ] Ensure package import itself performs no discovery.
- [ ] Add installed-fixture distribution tests.

## PLUG-003 — Runtime registries

**Status:** planned

**Dependencies:** PLUG-001, PLUG-002

- [ ] Implement runtime-owned category registries.
- [ ] Validate duplicate IDs, alias conflicts, incompatible API/core/IR versions, missing capabilities, and conflicting configuration ownership.
- [ ] Reject any descriptor claiming semantic-kernel, facet, selector, expression-root, or template-context extension capability.
- [ ] Implement exact ID and alias resolution.
- [ ] Remove all need for process-global decorator registries.

## PLUG-004 — Explicit least-authority contexts

**Status:** planned

**Dependencies:** PLUG-003, core ports

- [ ] Define least-authority construction contexts per category.
- [ ] Ensure target adapters receive only target/path descriptors, typed options, diagnostics, and immutable planned path inputs.
- [ ] Ensure engine adapters receive only template registry, immutable render context, safe helpers, diagnostics, and cache scope.
- [ ] Ensure source adapters receive controlled source access, closed-kernel builders/contracts, and no template/output services.
- [ ] Ensure providers/ecosystems/writers/executors receive only their documented ports.
- [ ] Test session isolation and no retained mutable context.

## PLUG-005 — Source adapter conformance suite

**Status:** planned

**Dependencies:** IR-001..IR-010, source port

- [ ] Test deterministic closed-kernel IR and digest.
- [ ] Test source spans, cancellation, in-memory loading, bounded references, and no source-type leakage.
- [ ] Test rejection of adapter-defined semantic objects, facets, selectors, expression roots, and context properties.
- [ ] Test bounded extension/raw size, type, and depth limits.
- [ ] Provide fixture base classes usable by `dryv-openapi` and third parties.

## PLUG-006 — Target/language adapter conformance suite

**Status:** planned

**Dependencies:** target path-validation port, typed options, PLAN-007

- [ ] Test target descriptors and longest-known extension inference.
- [ ] Test filename/reserved-name and declared candidate-identifier validation.
- [ ] Test destination-relative, project-path, package, namespace, index, and extension module-path facts.
- [ ] Test typed option schema, defaults, patches where permitted, introspection, and immutable inputs.
- [ ] Test that adapter outputs contain facts/diagnostics only.
- [ ] Prohibit rendered types, literals, comments, imports, exports, validators, decorators, formatting, or framework snippets.
- [ ] Prohibit semantic-kernel/selector/context extension.
- [ ] Allow capability-specific tests so adapters are not forced to claim unsupported validation/path features.

## PLUG-007 — Template-engine conformance suite

**Status:** planned

**Dependencies:** engine port, immutable render context, PLAN-005

- [ ] Test suffix inference, deterministic rendering, strict undefined behavior, immutable context, includes, cycles, limits, and diagnostics.
- [ ] Test denial of filesystem, environment, network, Python import, arbitrary callables, commands, and destination creation.
- [ ] Test cache invalidation by source/include/engine/helper version.
- [ ] Test rendering of template-authored import/type/validator/framework text without engine mutation or injection.

## PLUG-008 — Pack-provider conformance suite

**Status:** planned

**Dependencies:** pack provider port

- [ ] Test immutable resolution identity, containment, subdirectories, digests, cancellation, cache cleanup, and credential redaction.
- [ ] Cover local and Git provider common behavior.
- [ ] Ensure providers never inspect or modify semantic/template contracts.

## PLUG-009 — Ecosystem adapter conformance suite

**Status:** planned

**Dependencies:** ecosystem port, project/toolchain contracts

- [ ] Test known manifest detection, typed contributions, conflict handling, owned/contributed modes, action planning, and capability resolution.
- [ ] Ensure adapters never execute commands directly.
- [ ] Ensure ecosystem adapters cannot add semantic objects/facets/selectors or render application syntax.

## PLUG-010 — Writer/cache/executor conformance suites

**Status:** planned

**Dependencies:** writer/cache/executor ports

- [ ] Writer: staging, create/change/delete/leave, rollback, path safety, exact comparison, and ownership/generation-state records.
- [ ] Cache: content identity, isolation, corruption handling, bounds, and complete behavior keys.
- [ ] Executor: timeout, cancellation, environment filtering, capability enforcement, output capture, and process-tree cleanup.
- [ ] Prove generated output digests/state remain outside the dependency lock.

## PLUG-011 — Official/third-party parity

**Status:** planned

**Dependencies:** PLUG-005..PLUG-010

- [ ] Make official packages depend only on public conformance helpers.
- [ ] Add third-party fixture packages for every adapter category.
- [ ] Prove removing each official package makes only its format/target/engine/provider capability unavailable and does not break core import.
- [ ] Prove no official package has a hidden semantic-extension or syntax-rendering path.

## Acceptance gate

- Adapter discovery has no internal directory scanning or decorator side effects.
- Registry instances belong to runtimes/sessions.
- Official packages pass the exact public suites offered to third parties.
- No plugin can extend semantic objects, relations, facets, selectors, expression roots, contexts, or validators.
- No language adapter can author generated source syntax.
- Every descriptor and configuration conflict has a stable diagnostic.
