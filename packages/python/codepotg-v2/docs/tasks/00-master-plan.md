# CodepotG v2 master implementation plan

This plan implements only the approved v2 architecture. The old `packages/python/codepotg` package remains the old runtime; v2 does not add old configuration decoders, old execution paths, or imports from it.

## Stage 00 — Architecture and coordination

- [x] **DOC-001** Lock the approved two-file architecture, template-owned target rules, typed adapters, static files, authored barrels, bindings, commands, Git packs, and Python-first API.
- [x] **DOC-002** Define parallel-agent ownership, task states, progress evidence, and design-change policy.
- [x] **DOC-003** Document complete `codepotg.yaml` and `CodepotgPack.yaml` schemas.
- [x] **DOC-004** Document language, template-engine, source, pack-provider, and ecosystem adapter contracts.
- [x] **DOC-005** Document clean-room rewrite stages with no compatibility runtime.
- [ ] **DOC-006** Finish package-specific design/task expansion and verify no v2 task requests old decoders or old runtime imports.

## Stage 01 — Core foundation

- [ ] **CORE-001** Add isolated `pyproject.toml`, build metadata, supported Python versions, typing marker, and development/test dependencies.
- [ ] **CORE-002** Establish supported public namespaces and private module policy.
- [ ] **CORE-003** Implement semantic version, API version, IR version, plugin version, pack version, and behavior-version primitives.
- [ ] **CORE-004** Implement diagnostic codes, severities, source spans, related locations, and structured details.
- [ ] **CORE-005** Implement events, cancellation, operation/session IDs, result statuses, and immutable operation result bases.
- [ ] **CORE-006** Add import-direction, no-old-import, no-global-registry, and isolated-install architecture tests.

Exit gate: package installs/imports in a clean environment and core primitives have focused tests.

## Stage 02 — Typed configuration documents

- [ ] **CFG-001** Implement safe location-aware YAML and JSON syntax document nodes.
- [ ] **CFG-002** Reject duplicate keys and unsafe/unregistered YAML behavior.
- [ ] **CFG-003** Implement exact `(kind, apiVersion)` schema registry.
- [ ] **CFG-004** Implement typed decoder, validator, descriptor, and serializer protocols.
- [ ] **CFG-005** Implement schema introspection for configure, CLI, MCP, documentation, and editor tooling.
- [ ] **CFG-006** Prove raw mappings do not escape the configuration subsystem.

Exit gate: canonical v2 fixture documents decode with source spans; unsupported/unknown fields fail clearly.

## Stage 03 — Project contract

- [ ] **CFG-010** Implement project metadata, explicit `allow`, variables, and named sources.
- [ ] **CFG-011** Implement project units, toolchains, and package-manager selections.
- [ ] **CFG-012** Implement host/project security request models.
- [ ] **CFG-013** Implement global project before/after command declarations.
- [ ] **CFG-014** Implement ordered pack instances with local/Git locator types.
- [ ] **CFG-015** Implement per-instance source, profile, output, clean, options, bindings, overrides, and project-owned commands.
- [ ] **CFG-016** Add schema tests proving project-level `language`, `tasks`, `templateDir`, and internal template lists are invalid.

Exit gate: the full project specification example round-trips into immutable typed models.

## Stage 04 — Pack contract and discovery

- [ ] **PACKCFG-001** Implement pack metadata, compatibility, integration traits, content roots, ignore rules, and write policy.
- [ ] **PACKCFG-002** Implement public option, language-rule, engine-rule, binding, dependency, setup, command, and override-policy models.
- [ ] **PACKCFG-003** Implement named selections, file patterns, exact files, profiles, and declared outputs.
- [ ] **PACKCFG-004** Discover one descriptor per non-ignored source file.
- [ ] **PACKCFG-005** Infer template engine and target syntax by longest-known suffix.
- [ ] **PACKCFG-006** Classify template, authored barrel, static, binary, partial, and documentation roles.
- [ ] **PACKCFG-007** Implement Gitignore-compatible inline and file exclusions.
- [ ] **PACKCFG-008** Add tests proving no root barrel subsystem, no duplicate descriptors, static-by-default behavior, and no `paths.yaml` parser.

Exit gate: a heterogeneous pack containing TypeScript, Dart, YAML, Markdown, binary, static, partial, and barrel files validates.

## Stage 05 — Neutral IR and source adapter contract

- [ ] **IR-001** Implement provenance, semantic names, type expressions, schemas, fields, enums, operations, parameters, requests, responses, entities, and relationships.
- [ ] **IR-002** Define bounded extension/provenance points without leaking source-specific objects.
- [ ] **IR-003** Implement source adapter port, request/result, digest, and conformance suite.
- [ ] **IR-004** Add immutable IR and no-source-specific-import architecture tests.

Exit gate: an in-memory fake source adapter produces deterministic IR through only public contracts.

## Stage 06 — Plugin system

- [ ] **PLUG-001** Implement plugin descriptors, categories, versions, capabilities, and owned schema metadata.
- [ ] **PLUG-002** Implement Python entry-point discovery returning factories/descriptors.
- [ ] **PLUG-003** Implement runtime-owned instance registries and conflict validation.
- [ ] **PLUG-004** Implement explicit plugin construction contexts with least authority.
- [ ] **PLUG-005** Publish source, language, engine, ecosystem, pack-provider, writer, cache, executor, and event conformance bases.
- [ ] **PLUG-006** Add tests proving official plugins have no hidden core path and no import-time registration.

Exit gate: a third-party-style fixture plugin can be installed/discovered using only public APIs.

## Stage 07 — Rules, overrides, bindings, and imports

- [ ] **RULE-001** Implement rule field descriptors, typed full rules, typed patches, and supported merge operations.
- [ ] **RULE-002** Implement deterministic layer precedence and provenance inspection.
- [ ] **RULE-003** Implement host, adapter, pack, and project restriction hierarchy.
- [ ] **BIND-001** Implement binding catalog and template binding usage.
- [ ] **BIND-002** Implement module, project-path, package, namespace, barrel, text, value, package-name, artifact, and raw binding values.
- [ ] **BIND-003** Implement default barrels, binding groups, relative path planning, deduplication, and alias conflicts through language adapters.
- [ ] **BIND-004** Implement prompt, placeholder, omit, skip-template, and error missing policies plus strict readiness.

Exit gate: effective rules and imports are fully typed, explainable, deterministic, and free of raw deep merging.

## Stage 08 — Selection and planning

- [ ] **PLAN-001** Implement once, each, grouped, aggregate, and artifact-derived selections.
- [ ] **PLAN-002** Implement typed filter/order/group expressions.
- [ ] **PLAN-003** Implement folder-pattern fan-out for templates and static files.
- [ ] **PLAN-004** Implement template invocation, include, provider, artifact, import/export, output, pack, command, and contribution graphs.
- [ ] **PLAN-005** Implement cycle, missing/ambiguous provider, target compatibility, output collision, and path-safety validation.
- [ ] **PLAN-006** Implement authored barrel export context and multiple declared outputs.
- [ ] **PLAN-007** Implement immutable plan inspection and readiness statuses.

Exit gate: no renderer or writer is called for an invalid plan.

## Stage 09 — Runtime and rendering

- [ ] **RUN-001** Implement immutable runtime composition and isolated operation sessions.
- [ ] **RUN-002** Implement target adapter resolution per template invocation.
- [ ] **RUN-003** Implement engine adapter resolution per template invocation.
- [ ] **RUN-004** Implement immutable render context preparation and include compatibility.
- [ ] **RUN-005** Implement static/binary staging through the same artifact plan.
- [ ] **RUN-006** Implement sync/async cancellation and structured events.

Exit gate: a mixed-target in-memory pack renders through fake conforming adapters with no global state.

## Stage 10 — Writers and cache

- [ ] **WRITE-001** Implement memory writer.
- [ ] **WRITE-002** Implement archive writer.
- [ ] **WRITE-003** Implement transactional filesystem staging, exact comparison, path validation, backup, commit, and rollback.
- [ ] **WRITE-004** Implement managed/immutable/protected/unmanaged lifecycle handling and ownership manifest.
- [ ] **WRITE-005** Implement dry run and create/change/delete/leave reporting.
- [ ] **CACHE-001** Implement content-addressed cache with complete behavior keys and bounded materialization.

Exit gate: failures/cancellation before commit leave destination unchanged and all cache invalidation tests pass.

## Stage 11 — Commands, setup, dependencies, and toolchains

- [ ] **CMD-001** Implement security policy hierarchy and capability model.
- [ ] **CMD-002** Implement command/action plan, digest, approvals, environment allowlists, timeouts, and process cleanup.
- [ ] **CMD-003** Implement staged versus post-commit phases and honest transaction reporting.
- [ ] **SETUP-001** Implement typed setup questions, detection candidates, manual steps, and readiness actions.
- [ ] **ECO-001** Implement Node ecosystem adapter and npm/pnpm/Yarn capability resolution.
- [ ] **ECO-002** Implement Dart ecosystem adapter and pubspec/workspace contribution planning.
- [ ] **ECO-003** Implement owned versus contributed manifest behavior and dependency install policy.

Exit gate: server-safe policy denies execution; exact pack changes invalidate approvals; typed Node/Dart contributions pass tests.

## Stage 12 — Official adapters

- [ ] **OA-001+** Complete the detailed `codepotg-openapi` task ledger.
- [ ] **TS-001+** Complete the detailed TypeScript language adapter task ledger.
- [ ] **DART-001+** Complete the detailed Dart language adapter task ledger.
- [ ] **JINJA-001+** Complete the detailed Jinja engine task ledger.

Exit gate: each independent distribution passes core conformance and package-specific suites.

## Stage 13 — Official packs

- [ ] **PACK-TS-001+** Author TypeScript SDK pack through the new manifest and adapter contracts.
- [ ] **PACK-DART-001+** Author Dart SDK pack through the new manifest and adapter contracts.
- [ ] **PACK-FLUTTER-001+** Author Flutter SDK pack through the new manifest and adapter contracts.
- [ ] **PACK-INT-001** Prove full-project, standalone-folder, dependency-extension, and binding-fragment traits across fixtures.

Exit gate: realistic inspectable projects generate and validate using only v2 configuration.

## Stage 14 — Python API, configure, CLI, and MCP-ready operations

- [ ] **API-001** Implement high-level facade and typed requests/results.
- [ ] **API-002** Implement sync and async validate, inspect, plan, generate, configure, plugin, pack, cache, and approval operations.
- [ ] **CONFIGURE-001** Implement `codepotg configure`, per-pack configure, check mode, add-pack flow, and in-place project updates.
- [ ] **CLI-001** Implement thin CLI parsing/presentation and exit-code policy.
- [ ] **MCP-001** Publish structured serializable operations suitable for MCP/HTTP adapters.

Exit gate: API, CLI, and structured adapter paths call the same application services and return equivalent results.

## Stage 15 — Git packs, locking, and distribution

- [ ] **GIT-001** Implement local pack provider.
- [ ] **GIT-002** Implement generic Git and GitHub shorthand provider using existing Git credentials.
- [ ] **GIT-003** Implement safe immutable snapshot cache and subdirectory resolution.
- [ ] **LOCK-001** Implement `codepotg.lock` with requested refs, resolved commits, digests, plugin versions, and behavior versions.
- [ ] **LOCK-002** Tie pack command approvals to exact lock identity.
- [ ] **DIST-001** Publish minimal core distribution metadata.
- [ ] **DIST-002** Publish batteries-included `codepotg` dependency bundle.

Exit gate: public/private controlled fixtures resolve without storing credentials and fresh `pip install codepotg` has usable defaults.

## Stage 16 — Testing, re-authoring, and release

- [ ] **TEST-001** Complete architecture, unit, conformance, integration, property, and realistic fixture matrix.
- [ ] **REAUTHOR-001** Re-author representative project configs from old tasks into v2 sources/packs without runtime compatibility code.
- [ ] **REAUTHOR-002** Re-author representative old packs into `CodepotgPack.yaml` and classify intentional output differences.
- [ ] **PERF-001** Prove bounded behavior on large OpenAPI and large pack fixtures.
- [ ] **REL-001** Complete security review, documentation audit, package install matrix, versioning, and release checklist.

Exit gate: all official workflows run from a clean environment, docs match code, and no old generator dependency exists.
