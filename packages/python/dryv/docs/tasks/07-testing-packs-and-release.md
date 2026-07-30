# Testing, packs, cookbook, and release tasks

## TEST-001 — Test architecture

- [x] Unit tests focus on isolated rules and public contracts.
- [x] Reusable plugin behavior lives in conformance suites.
- [x] Integration tests use small connected vertical slices.
- [x] Architecture tests enforce dependency direction, closed-kernel ownership, no global registries, and template-owned output.
- [ ] Expand property tests for identity, paths, graph order, impact propagation, and cache keys.
- [ ] Keep tests independent from network, shared environment mutation, and execution order.

## TEST-002 — Configuration fixtures

- [x] Minimal and complete project fixtures.
- [x] Local, Git, mixed, and lock examples.
- [x] Heterogeneous template, static, binary, barrel, and partial pack fixtures.
- [x] Invalid fixtures for unknown fields, unsafe paths, conflicts, unsupported selectors, and command policy.
- [ ] Add Python contract-provider configuration fixtures after the public schema is implemented.

## TEST-003 — Closed-kernel connected fixture

- [x] Groups, object and enum schemas, operations, fields, tags, guidance, views, storage, policies, events, workflows, value sources, and presentations in focused variants.
- [x] TypeScript and Dart packs consuming the same contract.
- [x] Jinja options, bindings, selectors, imports, exports, symbols, partials, and static files.
- [x] Deterministic memory and managed filesystem generation.
- [ ] Expand into a realistic multi-pack application-system fixture.

## TEST-004 — Relationship validation

- [x] Missing schema and operation references.
- [x] Invalid group ownership.
- [x] Invalid storage, policy, event, view, value-source, and workflow relationships.
- [x] Unknown facets and invalid attachment locations.
- [ ] Add more related-location assertions and large connected invalid fixtures.

## TEST-005 — Planning and impact

- [x] Stable artifact identity separate from destination.
- [x] Provider matching by semantic identity, group scope, selection, and symbols.
- [x] No rendering for invalid plans.
- [ ] Complete artifact/symbol explanation traces.
- [ ] Add semantic blast-radius queries.
- [ ] Prove create/change/delete/leave causes through the public runtime API.

## TEST-006 — Managed filesystem safety

- [x] Create/change/delete/leave reporting.
- [x] Ownership state and manual-edit protection.
- [x] Unmanaged collision refusal.
- [x] Rollback-oriented transactional staging.
- [ ] Add injected failures at every commit phase.
- [ ] Expand Windows file-lock, interruption, and cancellation coverage.

## PACK-TS — TypeScript pack program

- [x] Connected manual SDK pack with schemas, enums, authored barrels, static configuration, and target validation.
- [x] Every TypeScript type, import, export, comment, and literal is template-authored.
- [x] Generated project passes `tsc --noEmit`.
- [ ] Add operations, failures, clients, errors, docs, and richer dependency fixtures.
- [ ] Package and version reusable official packs independently from the runtime.

## PACK-DART — Dart pack program

- [x] Connected manual Dart pack with schemas, enums, authored exports, and static configuration.
- [x] Every Dart type, import, export, annotation, and literal is template-authored.
- [x] Generated project passes Dart analysis.
- [ ] Add operations, clients, errors, serialization, and richer dependency fixtures.

## PACK-FLUTTER — Flutter integration program

- [ ] Keep Flutter policy in packs, never in the Dart target plugin.
- [ ] Consume neutral views, presentations, operations, schemas, policies, and workflows where present.
- [ ] Author all widgets, navigation, state, serialization, and validation syntax in templates.
- [ ] Declare assets, bindings, manual steps, and exact commands without adding UI framework roots to IR.

## PACK-SYSTEM — Application-system fixture

- [ ] Connect several groups, schemas, operations, storage mappings, policies, events, workflows, views, value sources, and presentations.
- [ ] Generate backend, SDK, mobile, workflow, storage, event, and documentation artifacts through separate packs.
- [ ] Verify generated dependencies through semantic identity and declared symbols.
- [ ] Change one semantic object and assert the exact impact graph.

## PERF-001 — Scale and bounds

- [ ] Test large Dryv contracts and relationship indexes with bounded memory.
- [ ] Test large pack discovery, artifact planning, render contexts, and impact queries.
- [ ] Test large artifacts, cache materialization, and cancellation latency.
- [ ] Publish reproducible fixture generators and commands.

## PERF-002 — Incremental equivalence

- [ ] Compare full and incremental output byte-for-byte.
- [ ] Use conservative fallback when context dependencies cannot be proven.
- [ ] Cover semantic, template, option, binding, target, engine, and provider changes.
- [ ] Keep generated output state outside `dryv.lock.yaml`.

## SEC-001 — Security review

- [ ] Plugin trust and kernel-extension denial.
- [ ] Jinja sandbox and immutable context authority.
- [ ] Git credential redaction and repository containment.
- [ ] Command approvals, environment, secrets, shell, network, and lifecycle scripts.
- [ ] Path traversal, symlinks, protected files, archives, cache, and state permissions.
- [ ] Regression tests for every accepted finding.

## COOKBOOK-001 — Practical documentation

Create executable recipes for:

- installation and first project;
- typed Python authoring;
- canonical IR inspection;
- local packs and `DryvPack.yaml`;
- Jinja templates and partials;
- TypeScript and Dart generation;
- options, bindings, selectors, imports, exports, and generated dependencies;
- plugin development and validation;
- managed output protection;
- deterministic and reproducible builds.

Each recipe includes goal, structure, files, commands, expected output, explanation, common failures, and the next recipe.

## REL-001 — Documentation conflict audit

- [ ] Search all Dryv source, tests, metadata, examples, and docs for archived names, removed packages, invalid selectors, duplicated transport ownership, and CLI logic in the runtime.
- [ ] Verify every active configuration field has a current example.
- [ ] Remove or clearly archive superseded prompts, audits, and progress records.
- [ ] Keep package task ledgers synchronized with actual implementation.

## REL-002 — Package matrix

- [ ] Build wheel/sdist for runtime, CLI, authoring, Jinja, TypeScript, and Dart packages.
- [ ] Test supported Python versions and available operating systems.
- [ ] Test runtime-only and full development installations.
- [ ] Test local, public Git, and controlled private Git pack resolution.
- [ ] Test CLI and Python examples from clean directories.
- [ ] Lock compatible dependency ranges.

## REL-003 — Release gate

Release is blocked unless:

- archived packages remain isolated;
- no compatibility decoder or removed package dependency remains;
- runtime and CLI responsibilities are separated;
- authoring feeds the runtime through an in-memory contract;
- the semantic kernel is closed and typed;
- templates own every emitted character;
- realistic generated TypeScript and Dart projects validate;
- planning and impact output is deterministic;
- full generation is proven before incremental generation;
- documentation, cookbook, tests, and progress evidence match the released code.
