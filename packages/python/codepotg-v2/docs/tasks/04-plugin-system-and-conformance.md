# Plugin system and conformance tasks

## PLUG-001 — Public plugin descriptors

**Status:** planned

**Dependencies:** CORE-002..CORE-005

- [ ] Define plugin category, ID, aliases, distribution, version, API version, IR constraints, capabilities, schema ownership, documentation, trust, and factory.
- [ ] Define category-specific descriptor extensions without private core imports.
- [ ] Validate descriptor immutability and serialization.

## PLUG-002 — Entry-point discovery

**Status:** planned

**Dependencies:** PLUG-001

- [ ] Discover each category through `importlib.metadata.entry_points`.
- [ ] Load descriptor factories lazily.
- [ ] Report broken distributions/entry points as diagnostics while keeping unrelated plugins available.
- [ ] Ensure package import itself performs no discovery.
- [ ] Add installed-fixture distribution tests.

## PLUG-003 — Runtime registries

**Status:** planned

**Dependencies:** PLUG-001, PLUG-002

- [ ] Implement runtime-owned category registries.
- [ ] Validate duplicate IDs, alias conflicts, incompatible API/IR versions, missing capabilities, and conflicting configuration ownership.
- [ ] Implement exact ID and alias resolution.
- [ ] Remove all need for module-global decorator registries.

## PLUG-004 — Explicit plugin contexts

**Status:** planned

**Dependencies:** PLUG-003, core ports

- [ ] Define least-authority construction contexts per category.
- [ ] Ensure language adapters do not receive writers/executors.
- [ ] Ensure engine adapters receive only template registry, safe helper registry, rules, diagnostics, and cache scope.
- [ ] Ensure source adapters receive controlled source access and no template/output services.
- [ ] Test session isolation and no retained mutable context.

## PLUG-005 — Source adapter conformance suite

**Status:** planned

**Dependencies:** IR-001..IR-004, source port

- [ ] Test deterministic IR and digest.
- [ ] Test source spans, cancellation, in-memory loading, bounded references, and no source-type leakage.
- [ ] Provide fixture base classes usable by `codepotg-openapi` and third parties.

## PLUG-006 — Language adapter conformance suite

**Status:** planned

**Dependencies:** RULE tasks, BIND tasks, language port

- [ ] Test target descriptors and extension inference.
- [ ] Test identifiers, reserved words, naming roles, declared type/literal/comment capabilities.
- [ ] Test module/project/package/barrel imports, relative paths, deduplication, ordering, and aliases.
- [ ] Test rule schema, defaults, patches, merge restrictions, introspection, and no IR mutation.
- [ ] Allow capability-specific tests so adapters are not forced to claim unsupported features.

## PLUG-007 — Template-engine conformance suite

**Status:** planned

**Dependencies:** engine port, render context, PLAN-005

- [ ] Test suffix inference, deterministic render, strict undefined behavior, immutable context, includes, cycles, limits, named outputs, and diagnostics.
- [ ] Test denial of filesystem, environment, network, Python import, arbitrary callables, and commands.
- [ ] Test cache invalidation by source/include/rule/helper version.

## PLUG-008 — Pack-provider conformance suite

**Status:** planned

**Dependencies:** pack provider port

- [ ] Test immutable resolution identity, containment, subdirectories, digests, cancellation, cache cleanup, and credential redaction.
- [ ] Cover local and Git provider common behavior.

## PLUG-009 — Ecosystem adapter conformance suite

**Status:** planned

**Dependencies:** ecosystem port, CFG toolchain contracts

- [ ] Test manifest detection, typed contributions, conflict handling, owned/contributed modes, action planning, and capability resolution.
- [ ] Ensure adapter never executes commands directly.

## PLUG-010 — Writer/cache/executor conformance suites

**Status:** planned

**Dependencies:** writer/cache/executor ports

- [ ] Writer: staging, create/change/delete/leave, rollback, path safety, exact comparison.
- [ ] Cache: content identity, isolation, corruption handling, bounds.
- [ ] Executor: timeout, cancellation, environment filtering, capability enforcement, output capture, process-tree cleanup.

## PLUG-011 — Official/third-party parity

**Status:** planned

**Dependencies:** PLUG-005..PLUG-010

- [ ] Make official packages depend only on public conformance helpers.
- [ ] Add a third-party fixture package in tests.
- [ ] Prove removing each official adapter makes only its capabilities unavailable and does not break core import.

## Acceptance gate

- Plugin discovery has no internal directory scanning or decorator side effects.
- Registry instances belong to runtimes/sessions.
- Official packages pass the exact public suites offered to third parties.
- Every descriptor and schema conflict has a stable diagnostic.
