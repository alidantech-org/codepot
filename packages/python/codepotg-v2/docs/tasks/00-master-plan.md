# CodepotG v2 master implementation plan

This plan implements only the approved v2 architecture and closed semantic kernel. The old `packages/python/codepotg` package remains the old runtime; v2 does not add old configuration decoders, old execution paths, or imports from it.

## Stage 00 — Architecture and coordination

- [x] **DOC-001** Lock the two-file project/pack architecture, filesystem discovery, static files, authored barrels, bindings, exact commands, direct Git packs, and Python-first API.
- [x] **DOC-002** Define parallel-agent ownership, task states, progress evidence, and design-change policy.
- [x] **DOC-003** Document complete `codepotg.yaml` and `CodepotgPack.yaml` schemas.
- [x] **DOC-004** Document source, target-validation, template-engine, pack-provider, and ecosystem adapter contracts.
- [x] **DOC-005** Document clean-room rewrite stages with no compatibility runtime.
- [x] **DOC-006** Align package-specific task ledgers with the simplified pack/project contract.
- [x] **DOC-007** Define the closed semantic kernel, root-first selectors, template-owned syntax, workflows/compensation, access, execution hooks, events, views, storage mappings, impact analysis, and incremental-generation boundary.

## Stage 01 — Core foundation

- [ ] **CORE-001** Add isolated `pyproject.toml`, build metadata, supported Python versions, typing marker, and development/test dependencies.
- [ ] **CORE-002** Establish supported public namespaces and private module policy.
- [ ] **CORE-003** Implement semantic version, API version, IR version, plugin version, pack version, naming behavior, selection behavior, and planning behavior primitives.
- [ ] **CORE-004** Implement diagnostic codes, severities, source spans, related locations, and structured details.
- [ ] **CORE-005** Implement events, cancellation, operation/session IDs, result statuses, and immutable operation result bases.
- [ ] **CORE-006** Add import-direction, no-old-import, no-global-registry, closed-kernel, and isolated-install architecture tests.

Exit gate: package installs/imports in a clean environment and core primitives have focused tests.

## Stage 02 — Typed configuration documents

- [ ] **CFG-001** Implement safe location-aware YAML and JSON syntax document nodes.
- [ ] **CFG-002** Reject duplicate keys and unsafe/unregistered YAML behavior.
- [ ] **CFG-003** Implement exact document-family/API-version schema registry.
- [ ] **CFG-004** Implement typed decoder, validator, descriptor, and serializer protocols.
- [ ] **CFG-005** Implement schema introspection for configure, CLI, MCP, documentation, and editor tooling.
- [ ] **CFG-006** Prove raw mappings do not escape the configuration subsystem.

Exit gate: canonical v2 fixtures decode with source spans; unsupported/unknown fields fail clearly.

## Stage 03 — Project contract

- [ ] **CFG-010** Implement project metadata, named semantic inputs, executables, security, and commands.
- [ ] **CFG-011** Implement project toolchain/package contexts only where real project integration requires them.
- [ ] **CFG-012** Implement host/project security request models.
- [ ] **CFG-013** Implement global project before/after command declarations.
- [ ] **CFG-014** Implement ordered pack instances with direct local/Git locator types.
- [ ] **CFG-015** Implement per-instance input, scalar output, options, bindings, executable overrides, and project-owned commands.
- [ ] **CFG-016** Add schema tests proving project-level `language`, `tasks`, `templateDir`, `registries`, `use`, and semantic-extension declarations are invalid.

Exit gate: the full project specification example round-trips into immutable typed models.

## Stage 04 — Pack contract and discovery

- [ ] **PACKCFG-001** Implement pack metadata, compatibility, include/exclude rules, options, bindings, executables, and exact commands.
- [ ] **PACKCFG-002** Implement one `selections` emission registry using fixed root-first selectors, paths, imports, exports, bindings, and symbols.
- [ ] **PACKCFG-003** Reject pack-defined facets, semantic roots, selector queries, arbitrary traversal, language-rendered syntax rules, and invented semantic filenames.
- [ ] **PACKCFG-004** Discover one descriptor per non-ignored source file under `templates/`.
- [ ] **PACKCFG-005** Infer template engine and target syntax by longest-known suffix.
- [ ] **PACKCFG-006** Classify template, authored barrel, static, binary, partial, and documentation files.
- [ ] **PACKCFG-007** Implement Gitignore-compatible inline and file exclusions.
- [ ] **PACKCFG-008** Add tests proving no root barrel subsystem, no duplicate descriptors, static-by-default behavior, and no `paths.yaml` parser.

Exit gate: heterogeneous packs validate and cannot redefine semantic meaning or emitted-syntax ownership.

## Stage 05 — Closed semantic kernel and source adapter contract

- [ ] **IR-001** Implement source-neutral provenance and stable semantic identity.
- [ ] **IR-002** Implement naming projections, structural schema kinds, fields, constraints, and neutral type expressions.
- [ ] **IR-003** Implement groups and schema-use relationships.
- [ ] **IR-004** Implement operation inputs, outputs, failures, effects, and references.
- [ ] **IR-005** Implement the closed known facet registry and attachment validation.
- [ ] **IR-006** Implement views, storage mappings, access policies, and effective access resolution.
- [ ] **IR-007** Implement events, listeners, and execution-hook relationships.
- [ ] **IR-008** Implement workflows, steps, transitions, waits, decisions, parallel branches, and compensation.
- [ ] **IR-009** Implement bounded extensions/raw provenance without semantic extension.
- [ ] **IR-010** Implement uniform kernel validation and private typed graph indexes.
- [ ] **SOURCE-001** Define source adapter port, request/result, digest, and conformance suite.
- [ ] **SOURCE-002** Add immutable IR and no-source-specific-import/no-kernel-extension architecture tests.

Exit gate: an in-memory fake source adapter produces and validates deterministic closed-kernel IR through only public contracts.

## Stage 06 — Adapter/plugin system

- [ ] **PLUG-001** Implement adapter descriptors, categories, versions, capabilities, configuration ownership, trust, and factories.
- [ ] **PLUG-002** Implement Python entry-point discovery returning factories/descriptors.
- [ ] **PLUG-003** Implement runtime-owned instance registries and conflict validation.
- [ ] **PLUG-004** Implement explicit least-authority construction contexts.
- [ ] **PLUG-005** Publish source, target-validation, engine, ecosystem, pack-provider, writer, cache, executor, and event conformance bases.
- [ ] **PLUG-006** Add tests proving adapters cannot register semantic objects, facets, selectors, expression roots, or emitted syntax services.

Exit gate: a third-party fixture adapter installs/discovers through public APIs without semantic-kernel extension or hidden core access.

## Stage 07 — Options, bindings, and generated dependencies

- [ ] **RULE-001** Implement typed full option/rule objects, typed patches where permitted, and supported merge operations.
- [ ] **RULE-002** Implement deterministic layer precedence and provenance inspection.
- [ ] **RULE-003** Implement host, adapter, pack, and project restriction hierarchy.
- [ ] **BIND-001** Implement external binding catalog and selection/template usage.
- [ ] **BIND-002** Implement module, project-path, package, namespace, text, value, package-name, and artifact binding values.
- [ ] **BIND-003** Implement generated provider matching by semantic identity, scope, selection key, and declared symbols.
- [ ] **BIND-004** Implement unresolved binding policies and strict readiness.

Exit gate: generated dependencies and external bindings are typed, explicit, deterministic, and expose facts rather than emitted statements.

## Stage 08 — Selection, artifact planning, explain, and impact

- [ ] **PLAN-001** Implement filesystem discovery descriptors.
- [ ] **PLAN-002** Implement versioned root-first `.each`/`.all` fixed selectors and active-parent contexts.
- [ ] **PLAN-003** Implement selection-folder fan-out for templates/static/binary files.
- [ ] **PLAN-004** Implement stable invocation and artifact identity separate from destination.
- [ ] **PLAN-005** Implement include/partial graph.
- [ ] **PLAN-006** Implement selection dependency, semantic provider, symbol, export, and ordering graph.
- [ ] **PLAN-007** Implement immutable provider/consumer/path/module descriptors for template-authored imports/exports.
- [ ] **PLAN-008** Implement output/collision/path-safety graph.
- [ ] **PLAN-009** Implement commands, approvals, unresolved actions, and readiness.
- [ ] **PLAN-010** Implement plan inspection, artifact/symbol explanation, and serialization.
- [ ] **PLAN-011** Implement semantic-to-artifact impact and blast-radius graph.
- [ ] **PLAN-012** After full generation is proven, implement conservative incremental generation with complete-generation equivalence.

Exit gate: no renderer/writer is called for an invalid semantic or artifact plan; every artifact is explainable.

## Stage 09 — Runtime and rendering

- [ ] **RUN-001** Implement immutable runtime composition and isolated sessions.
- [ ] **RUN-002** Resolve one target descriptor/validator per template invocation.
- [ ] **RUN-003** Resolve one engine adapter per template invocation.
- [ ] **RUN-004** Prepare immutable render contexts containing only documented kernel, planning, option, binding, and dependency values.
- [ ] **RUN-005** Implement static/binary staging through the same artifact plan.
- [ ] **RUN-006** Implement sync/async cancellation and structured events.
- [ ] **RUN-007** Add architecture tests proving only templates/macros/partials/static files author emitted source text.

Exit gate: a mixed-target in-memory pack renders through fake conforming adapters with no global state or adapter-authored syntax.

## Stage 10 — Writers, ownership state, and cache

- [ ] **WRITE-001** Implement memory writer.
- [ ] **WRITE-002** Implement archive writer.
- [ ] **WRITE-003** Implement transactional filesystem staging, exact comparison, path validation, backup, commit, and writer rollback.
- [ ] **WRITE-004** Implement managed/immutable/protected/unmanaged lifecycle handling and ownership/generation-state manifest.
- [ ] **WRITE-005** Implement dry run and create/change/delete/leave reporting with semantic causes.
- [ ] **CACHE-001** Implement content-addressed cache with complete behavior keys and bounded materialization.
- [ ] **CACHE-002** Store output digests and incremental state outside `codepotg.lock.yaml`.

Exit gate: failures/cancellation before commit leave destination unchanged and all cache/state invalidation tests pass.

## Stage 11 — Commands and project ecosystems

- [ ] **CMD-001** Implement security policy hierarchy and capability model.
- [ ] **CMD-002** Implement command plan, digest, approvals, environment allowlists, timeouts, and process cleanup.
- [ ] **CMD-003** Implement staged versus post-commit phases and honest transaction reporting.
- [ ] **SETUP-001** Implement typed setup questions, detection candidates, manual steps, and readiness actions.
- [ ] **ECO-001** Implement known Node project/toolchain inspection and contribution planning.
- [ ] **ECO-002** Implement known Dart project/toolchain inspection and contribution planning.
- [ ] **ECO-003** Keep package-manager command syntax in authored commands and project ecosystem code, never in semantic core.

Exit gate: server-safe policy denies execution; exact pack changes invalidate approvals; project contributions are typed and explicit.

## Stage 12 — Official adapters

- [ ] **OA-001+** Complete the aligned `codepotg-openapi` ledger, including typed `x-codegen` mapping into the closed kernel.
- [ ] **TS-001+** Complete the TypeScript target detection/validation/path package without syntax renderers.
- [ ] **DART-001+** Complete the Dart target detection/validation/path package without syntax renderers.
- [ ] **JINJA-001+** Complete the Jinja engine ledger.

Exit gate: each distribution passes public conformance and closed-kernel/non-rendering boundaries.

## Stage 13 — Official packs

- [ ] **PACK-TS-001+** Author TypeScript SDK pack using group-rooted schema/operation selections and fully authored TypeScript syntax.
- [ ] **PACK-DART-001+** Author Dart SDK pack using the same semantic kernel with fully authored Dart syntax.
- [ ] **PACK-FLUTTER-001+** Author Flutter integration pack using views/operations/schemas where present and fully authored Flutter/Dart syntax.
- [ ] **PACK-INT-001** Prove storage, views, access, events, workflows, compensation, listeners, and generated dependency connections through inspectable fixtures.

Exit gate: realistic inspectable projects generate and validate using only v2 configuration and template-authored output.

## Stage 14 — Python API, configure, CLI, IDE/MCP-ready operations

- [ ] **API-001** Implement high-level facade and typed requests/results.
- [ ] **API-002** Implement sync/async validate, inspect, plan, impact, generate, configure, plugin, pack, cache, and approval operations.
- [ ] **CONFIGURE-001** Implement configure/check/add-pack flows and in-place project updates.
- [ ] **CLI-001** Implement thin CLI parsing/presentation and exit-code policy.
- [ ] **MCP-001** Publish structured serializable operations suitable for MCP/HTTP adapters.
- [ ] **IMPACT-UI-001** Define IDE/web blast-radius data contract after PLAN-011 is stable.

Exit gate: API, CLI, and structured adapters call the same services and return equivalent plans/impact data.

## Stage 15 — Git packs, locking, and distribution

- [ ] **GIT-001** Implement local pack provider.
- [ ] **GIT-002** Implement generic Git provider using existing Git credentials.
- [ ] **GIT-003** Implement safe immutable snapshot cache and subdirectory resolution.
- [ ] **LOCK-001** Implement `codepotg.lock.yaml` with requested refs, resolved commits, digests, plugin versions, and behavior versions.
- [ ] **LOCK-002** Tie downloaded command approvals to exact lock identity.
- [ ] **LOCK-003** Prove generated output hashes/state are excluded from the dependency lock.
- [ ] **DIST-001** Publish minimal core distribution metadata.
- [ ] **DIST-002** Publish batteries-included dependency bundle.

Exit gate: public/private controlled fixtures resolve without storing credentials and fresh installation has usable defaults.

## Stage 16 — Testing, re-authoring, and release

- [ ] **TEST-001** Complete architecture, unit, conformance, integration, property, realistic semantic, and generated-project verification matrix.
- [ ] **REAUTHOR-001** Re-author representative project configs without runtime compatibility code.
- [ ] **REAUTHOR-002** Re-author representative packs using group-rooted selectors and template-authored syntax.
- [ ] **PERF-001** Prove bounded behavior on large OpenAPI, semantic graphs, pack discovery, planning, and impact fixtures.
- [ ] **REL-001** Complete security review, documentation conflict audit, package install matrix, versioning, and release checklist.

Exit gate: official workflows run from a clean environment, docs match code, no old generator dependency exists, no conflicting semantic vocabulary remains, and deterministic full generation is proven before incremental mode is enabled.
