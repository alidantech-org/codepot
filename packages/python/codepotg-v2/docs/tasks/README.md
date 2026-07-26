# CodepotG v2 task tracking

This folder is the implementation control plane for the clean rewrite. Design documents define what must exist; task files define exact work, dependencies, acceptance criteria, ownership, and proof.

## Mandatory rules

- Read `../00-governance/00-approved-architecture.md` before claiming work.
- Read `../03-generation/00-path-expressions-and-name-tokens.md` before changing pack discovery, output planning, IR names, language filename rules, or official packs.
- V2 tasks must not add old `tasks`, project-level `language`, `templateDir`, `paths.yaml` parsing, old runtime imports, or fallback execution.
- Do not add `fileName`, `filePath`, `directory`, or equivalent output conveniences to semantic IR records.
- Claim work in `PARALLEL_WORK.md` before editing implementation files.
- Use task IDs in commits and progress notes.
- One active owner per task.
- Mark a task complete only after implementation, focused tests, architecture/conformance tests, documentation, and progress evidence are complete.

## Status representation

```text
- [ ] incomplete
- [x] complete

Status: planned | claimed | in_progress | blocked | review | complete | superseded
```

A checkbox never substitutes for task state and evidence.

## Required task fields

Every implementation task identifies:

- task ID and title;
- owning package/subsystem;
- dependencies by task ID;
- intended files/directories;
- implementation requirements;
- prohibited shortcuts;
- focused tests;
- acceptance criteria;
- documentation updates;
- progress evidence.

## Task files

- `00-master-plan.md` — staged program-level plan.
- `01-core-foundation-and-api.md` — package, diagnostics, events, runtime, and Python API.
- `02-configuration-and-pack-contracts.md` — typed project/pack schemas, rules, overrides, bindings, setup, commands, and toolchains.
- `03-ir-selection-and-planning.md` — neutral IR, pack files, selections, graphs, imports, readiness.
- `04-plugin-system-and-conformance.md` — plugin protocols, discovery, registries, and shared suites.
- `05-writers-cache-and-security.md` — transactional writers, cache, commands, approvals, manifests.
- `06-configure-cli-git-and-distribution.md` — configure workflow, CLI, MCP-ready API, Git packs, locking, distributions.
- `07-testing-packs-and-release.md` — official adapters/packs, fixtures, re-authoring, quality gates, release.
- `08-path-expressions-and-naming.md` — semantic name projections, `{recipe}` and `[expression]` syntax, source-path compilation, and path conformance.
- `PARALLEL_WORK.md` — active ownership and lane coordination.
- `PROGRESS.md` — append-only evidence log.

Package-specific work is further decomposed in each package's `docs/tasks` folder.

## Completion evidence

A completed task records:

```text
Commit: <sha>
Tests: <exact commands and results>
Docs: <updated paths>
Acceptance: <criteria confirmed>
Follow-up: <next task or none>
```

Do not write “tests passed” without the exact command. Do not claim runtime tests for documentation-only commits.
