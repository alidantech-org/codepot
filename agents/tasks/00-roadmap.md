# Codepot implementation roadmap

## Phase status

| Order | Phase | Status | Issue | Gate |
|---|---|---|---|---|
| 00 | Agent guides and task system | [x] | #2 closed | Complete |
| 01 | Shared contract and stable artifacts | [ ] | #3 | Phase 00 complete |
| 02 | Runtime and platform adapters | [ ] | Open when ready | Phase 01 complete |
| 03 | Authoring parity and canonical compiler | [ ] | Open when ready | Required Phase 01/02 ports complete |
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

## Global completion conditions

- every phase has compatibility and behavioral validation;
- stable artifacts are versioned and deterministic;
- old TypeScript contracts work with import-only migration where expected;
- Python generator behavior is intentionally ported to Handlebars/TypeScript;
- no domain layer performs un-injected filesystem, process, Git, cache, or terminal work;
- external CLI contains no domain logic;
- package export and consumer-fixture checks pass.
