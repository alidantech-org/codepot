# Codepot implementation roadmap

## Phase status

| Order | Phase | Status | Issue | Gate |
|---|---|---|---|---|
| 00 | Agent guides and task system | [x] | #2 closed | Complete |
| 01 | Shared contract and stable artifacts | [x] | #3 closed | Complete |
| 02 | Runtime and platform adapters | [x] | #4 closed | Complete |
| 03 | Authoring parity and canonical compiler | [~] | #5 | In progress |
| 04 | Templating and Handlebars migration | [ ] | Open when ready | Stable artifacts and platform ports complete |
| 05 | Generation and CodepotFile orchestration | [ ] | Open when ready | Authoring and templating ports usable |
| 06 | External CLI frontend | [ ] | Open when ready | Runtime generation path stable |
| 07 | Integration, parity, packaging, release | [ ] | Open when ready | Phases 01-06 complete |

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

The stable authoring artifact, engine ports, platform ports, requests, results, diagnostics, and events are designed before concrete implementations.

## Phase 00 validation

Status: [x]
Issue: #2 closed as completed
Depends on: repository package foundation
Commit: `4415c31bd3aed17f6286dc9c8c94226cea217e30`
Validation: GitHub content reads verified `AGENTS.md`, this roadmap, and `01-contract.md`; commit comparison verified the complete `agents/` and `agents/tasks/` file set and removal of temporary `.keep` files.

- [x] Root `AGENTS.md` instructions committed.
- [x] Project, architecture, rules, workflow, and features guides committed.
- [x] Ordered task files committed.
- [x] GitHub issue workflow documented.
- [x] First contract issue opened as #3.
- [x] Files committed to `chatgpt/codepotx-restart`.
- [x] Paths and contents verified from GitHub.
- [x] Issue #2 closed.

## Phase 01 validation

Status: [x]
Issue: #3 closed as completed
Depends on: Phase 00
Commits: `b5b2624a356c902ab4185f59bc2d2f37aefefa4f`, `7d5b44d9ee5f55e351db1d8bd96b2ee85006f71a`
Validation: strict TypeScript typecheck and declaration emission passed; GitHub comparisons and content reads verified all stable artifact, request, result, port, event, runtime, package-export, and build-entry changes.

- [x] Stable authoring, template-pack, generation-plan, and rendered-generation artifacts defined.
- [x] Authoring, templating, generation, platform, event, and runtime ports defined.
- [x] Runtime operation mapping covers every engine operation.
- [x] `codepotx/contract` export configured.
- [x] Issue #3 closed.

## Phase 02 validation

Status: [x]
Issue: #4 closed as completed
Depends on: Phase 01
Commits: `eea311de78bb32cdf27b0444850cc0169c471bd7`, `46add634861b1e29c54cf4669c9c572fd9ca1b31`, `0217170f27a2e45c6b1b551aca9757253e8b5073`, `90b716289bb4f9e65d655ec7b806fb2fa7f73a60`
Validation: strict checks and declaration emission passed; 13 focused runtime/platform tests passed; GitHub comparisons verified all implementation, test, export, and package wiring changes.

- [x] Explicit DI runtime and typed operation dispatch implemented.
- [x] Ordered observation-only events and per-run context implemented.
- [x] Node and memory platform services implemented.
- [x] Filesystem, writer, codec, hash, cache, command, module, and source adapters implemented.
- [x] Local, package, Git, artifact, and memory source modes implemented.
- [x] `codepotx/runtime` and `codepotx/platform` exports configured.
- [x] Issue #4 closed.

## CodepotX structure hardening track

The implemented top-level architecture remains valid, but internal compiler and orchestration modules must be reorganized before further large-scale feature growth.

Source of truth: `agents/CODEPOTX_STRUCTURE_GUIDE.md`.

| Order | Task | Status | Gate |
|---|---|---|---|
| 15 | Structure migration program | [~] | Tasks 17-20 combined validation active |
| 16 | Baseline and architecture guardrails | [x] | #14 closed; 40 library and 3 CLI tests passed with package validation |
| 17 | Contract partitioning | [~] | #15; strict type gate passed, combined validation pending |
| 18 | Authoring modularization | [~] | #16; implementation complete, combined validation pending |
| 19 | Templating modularization | [~] | #17; implementation complete, combined validation pending |
| 20 | Generation modularization | [~] | #18; implementation complete, combined validation pending |
| 21 | Runtime and platform modularization | [ ] | Tasks 17-20 complete |
| 22 | Tests, exports, documentation, and cleanup | [ ] | Task 21 complete |
| 23 | Full structural integration gate | [ ] | Tasks 16-22 complete |

No broad source move may begin before Task 16 captures the baseline and adds architecture checks. Each phase requires its own issue, focused commits, validation evidence, and issue closure.

## Global completion conditions

- every phase has compatibility and behavioral validation;
- stable artifacts are versioned and deterministic;
- old TypeScript contracts work with import-only migration where expected;
- Python generator behavior is intentionally ported to Handlebars/TypeScript;
- no domain layer performs un-injected filesystem, process, Git, cache, or terminal work;
- external CLI contains no domain logic;
- package export and consumer-fixture checks pass;
- Tasks 15-23 complete the non-breaking structure hardening program before unrestricted feature expansion.
