# CodepotG v2 task tracking

This folder is the implementation control plane for the clean rewrite. Design documents define what must exist; task files define the exact work, dependencies, acceptance criteria, ownership, and proof required to mark it complete.

## Mandatory rules

- Read `../00-governance/00-approved-architecture.md` before claiming work.
- V2 tasks must not add old `tasks`, project-level `language`, `templateDir`, `paths.yaml` parsing, old runtime imports, or fallback execution.
- Claim work in `PARALLEL_WORK.md` before editing implementation files.
- Use task IDs in commits and progress notes.
- One active owner per task.
- Mark a task complete only after implementation, focused tests, architecture/conformance tests, documentation, and progress records are complete.

## Status representation

Checkbox:

```text
- [ ] incomplete
- [x] complete
```

State annotation:

```text
**Status:** planned | claimed | in_progress | blocked | review | complete | superseded
```

A checkbox is never used as a substitute for the state and evidence fields.

## Required task fields

Every implementation task must identify:

- task ID and title;
- owning package/subsystem;
- dependencies by task ID;
- intended files or directories;
- implementation requirements;
- prohibited shortcuts;
- focused tests;
- acceptance criteria;
- documentation updates;
- progress evidence.

## Task files

- `00-master-plan.md` — staged program-level plan.
- `01-core-foundation-and-api.md` — package, diagnostics, events, runtime, and Python API.
- `02-configuration-and-pack-contracts.md` — typed project/pack schemas, rules, overrides, bindings, setup, commands, toolchains.
- `03-ir-selection-and-planning.md` — neutral IR, pack files, selections, graphs, imports, readiness.
- `04-plugin-system-and-conformance.md` — plugin protocols, discovery, registries, shared suites.
- `05-writers-cache-and-security.md` — transactional writers, cache, commands, approvals, manifests.
- `06-configure-cli-git-and-distribution.md` — configure workflow, CLI, MCP-ready API, Git packs, locking, distributions.
- `07-testing-packs-and-release.md` — official adapters/packs, fixtures, re-authoring, quality gates, release.
- `PARALLEL_WORK.md` — active ownership and lane coordination.
- `PROGRESS.md` — append-only evidence log.

Package-specific work is further decomposed in each package's own `docs/tasks` folder.

## Completion evidence

A completed task records:

```text
Commit: <sha>
Tests: <exact commands and results>
Docs: <updated paths>
Acceptance: <criteria confirmed>
Follow-up: <next task or none>
```

Do not use “tests passed” without listing the command. Do not claim runtime tests for documentation-only commits.
