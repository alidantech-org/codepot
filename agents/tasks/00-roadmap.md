# Codepot implementation roadmap

## Phase status

| Order | Phase | Status | Issue | Gate |
|---|---|---|---|---|
| 00 | Agent guides and task system | [~] | #2 | Documentation committed and verified |
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

Status: [~]
Issue: #2
Depends on: repository package foundation
Commit: pending
Validation: pending repository file and PR verification

- [x] Root `AGENTS.md` instructions drafted.
- [x] Project, architecture, rules, workflow, and features guides drafted.
- [x] Ordered task files drafted.
- [x] GitHub issue workflow documented.
- [x] First contract issue opened as #3.
- [ ] Files committed to `chatgpt/codepotx-restart`.
- [ ] Paths and contents verified from GitHub.
- [ ] Issue #2 closed.

## Global completion conditions

- every phase has compatibility and behavioral validation;
- stable artifacts are versioned and deterministic;
- old TypeScript contracts work with import-only migration where expected;
- Python generator behavior is intentionally ported to Handlebars/TypeScript;
- no domain layer performs un-injected filesystem, process, Git, cache, or terminal work;
- external CLI contains no domain logic;
- package export and consumer-fixture checks pass.
