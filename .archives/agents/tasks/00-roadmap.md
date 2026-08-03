# Codepot implementation roadmap

## Phase status

| Order | Phase | Status | Issue | Gate |
|---|---|---|---|---|
| 00 | Agent guides and task system | [x] | #2 closed | Complete |
| 01 | Shared contract and stable artifacts | [x] | #3 closed | Complete |
| 02 | Runtime and platform adapters | [x] | #4 closed | Complete |
| 03 | Authoring parity and canonical compiler | [~] | #5 | In progress |
| 04 | Templating and Handlebars migration | [x] | #6 closed | Complete baseline |
| 05 | Generation and CodepotFile orchestration | [x] | #7 closed | Complete baseline |
| 06 | External CLI frontend | [x] | completed baseline | Complete baseline |
| 07 | Integration, parity, packaging, release | [x] | completed baseline | Complete baseline |
| 08 | Template variable contract and validation | [x] | #10 closed | Complete baseline |
| 09 | Production-grade generation hardening | [ ] | Open after Task 24 direction gates | Task 24 architecture decisions |

## Architectural commitment

```text
shared contract
      ↓
runtime + platform
      ↓
authoring and templating
      ↓
generation
      ↓
external CLI and other frontends
```

Stable artifacts, ports, requests, results, diagnostics, and events are designed before concrete implementations. New generation work must also keep large source records and rendered blobs outside unbounded in-memory plans.

## Completed foundation

- [x] Phase 00 agent/task system and issue workflow.
- [x] Phase 01 stable artifacts, ports, operations, diagnostics, events, and contract exports.
- [x] Phase 02 explicit-DI runtime, typed dispatch baseline, ordered events, and Node/memory adapters.
- [x] Baseline templating, generation, CLI, release, and template-variable behavior.

## CodepotX structure hardening track

Source of truth: `agents/CODEPOTX_STRUCTURE_GUIDE.md`.
Final audit: `agents/audits/CODEPOTX_STRUCTURE_FINAL.md`.

| Order | Task | Status | Gate |
|---|---|---|---|
| 15 | Structure migration program | [~] | Tasks 16–23 implemented; final combined gate pending |
| 16 | Baseline and architecture guardrails | [x] | #14 closed |
| 17 | Contract partitioning | [x] | #15 closed; combined package gate passed |
| 18 | Authoring modularization | [x] | #16 closed; combined package gate passed |
| 19 | Templating modularization | [x] | #17 closed; combined package gate passed |
| 20 | Generation modularization | [x] | #18 closed; combined package gate passed |
| 21 | Runtime and platform modularization | [~] | #19 open; implementation complete, final gate pending |
| 22 | Tests, exports, documentation, and cleanup | [~] | #20 open; implementation complete, final gate pending |
| 23 | Full structural integration gate | [~] | #21 open; audit and guardrails committed, execution pending |

Tasks 16–20 passed strict source/test typechecks, 45 CodepotX tests, 3 CLI tests, package builds, Publint, and ESM package-resolution checks. Tasks 21–23 add typed runtime dispatch, capability-owned platform adapters, grouped tests, explicit package exports, consumer fixtures, final documentation, and the integration audit.

## CodepotG JSONL-first lazy generation track

Source of truth: `agents/tasks/24-codepotg-jsonl-lazy-generation.md`.

| Order | Gate | Status | Required outcome |
|---|---|---|---|
| 24.1 | JSONL compiler foundation | [ ] | JSON-first streaming extraction without a full OpenAPI object |
| 24.2 | Headless indexes | [ ] | Direct ref/resource/dependency/mention lookup with bounded hot indexes |
| 24.3 | Queue pipeline | [ ] | Bounded reader, parser, planner, resolver, writer, and event queues |
| 24.4 | Selection planning | [ ] | Lazy selection and virtual output registry without full rendered plans |
| 24.5 | Human `paths.yaml` approval | [!] | No final syntax or implementation before explicit approval |
| 24.6 | Dependencies and barrels | [ ] | Explicit providers, overlap validation, and dynamic barrel scheduling |
| 24.7 | Context and imports | [ ] | Correct selection-specific lazy context and registry-backed imports |
| 24.8 | Documentation and release gate | [ ] | Complete selection, variable, template, and `paths.yaml` author guides |

The JSONL compiler foundation is the first compilation change. `paths.yaml` design work may inventory and propose alternatives, but the final direction requires human approval.

## Final structure gate

```bash
pnpm --filter codepotx check
pnpm --filter codepotx-cli check
pnpm check
pnpm build
```

## Global completion conditions

- every phase has compatibility and behavioral validation;
- stable artifacts are versioned and deterministic;
- old TypeScript contracts work with import-only migration where expected;
- useful Python generator behavior is preserved or intentionally evolved;
- no domain layer performs un-injected filesystem, process, Git, cache, or terminal work;
- external CLI contains no domain logic;
- package export and consumer-fixture checks pass;
- large OpenAPI inputs compile without requiring the full document in memory;
- bounded queues and indexes prevent parser, planner, renderer, writer, or logger memory growth;
- template authors can inspect all supported selections, variables, contexts, and dependency-provider rules;
- Tasks 15–23 complete the non-breaking structure hardening program before unrestricted CodepotX feature expansion;
- Task 24 is implemented in ordered gates, with explicit human approval for the `paths.yaml` contract.
