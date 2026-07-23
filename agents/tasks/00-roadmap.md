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
| 07 | Integration, parity, packaging, release | [ ] | Open when ready | Phases 01–06 complete |

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

## Completed foundation

- [x] Phase 00 agent/task system and issue workflow.
- [x] Phase 01 stable artifacts, ports, operations, diagnostics, events, and contract exports.
- [x] Phase 02 explicit-DI runtime, typed dispatch baseline, ordered events, and Node/memory adapters.

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
- Python generator behavior is intentionally ported to Handlebars/TypeScript;
- no domain layer performs un-injected filesystem, process, Git, cache, or terminal work;
- external CLI contains no domain logic;
- package export and consumer-fixture checks pass;
- Tasks 15–23 complete the non-breaking structure hardening program before unrestricted feature expansion.
