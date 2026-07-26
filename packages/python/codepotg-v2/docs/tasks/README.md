# CodepotG v2 task tracking

This folder is the implementation control plane for the clean rewrite. Design documents define what must exist; task files define exact work, dependencies, acceptance criteria, ownership, and proof.

## Mandatory rules

- Read `../00-governance/00-approved-architecture.md` before claiming work.
- Read `../02-configuration/02-pack-manifest-specification.md` before changing pack configuration.
- Read `../03-generation/00-path-expressions-and-name-tokens.md` before changing discovery, selectors, paths, names, imports/exports, or official packs.
- Read `../05-distribution/02-git-github-locking-and-trust.md` before changing local/Git providers or locks.
- V2 tasks must not add old `tasks`, project-level `language`, `templateDir`, `paths.yaml`, `registries`, `use`, old runtime imports, or fallback execution.
- Do not add `fileName`, `filePath`, `directory`, or equivalent output conveniences to semantic IR records.
- Do not restore root pack `paths`, `files`, or `filePatterns`; ordinary content is filesystem-discovered and explicit emissions are registered under `selections`.
- Claim implementation work in `PARALLEL_WORK.md` before editing implementation files.
- Use task IDs in commits and progress notes.
- One active owner per task.
- Mark a task complete only after implementation, focused tests, architecture/conformance tests, documentation, and evidence are complete.

## Status representation

```text
- [ ] incomplete
- [x] complete

Status: planned | claimed | in_progress | blocked | review | complete | superseded
```

A checkbox never substitutes for task state and evidence.

## Required task fields

Every implementation task identifies:

- task ID/title;
- owner/package;
- dependencies;
- intended files;
- requirements and prohibited shortcuts;
- focused tests;
- acceptance criteria;
- documentation and progress evidence.

## Task files

- `00-master-plan.md` — staged program-level plan.
- `01-core-foundation-and-api.md` — packages, diagnostics, events, runtime, and Python API.
- `02-configuration-and-pack-contracts.md` — simplified project/pack schemas, executable/command contracts, selections, imports/exports, and bindings.
- `03-ir-selection-and-planning.md` — neutral IR, fixed selectors, planning graphs, imports, readiness, and artifacts.
- `04-plugin-system-and-conformance.md` — plugin protocols, discovery, registries for installed plugins, and shared suites.
- `05-writers-cache-and-security.md` — transactional writers, cache, exact commands, approvals, and manifests.
- `06-configure-cli-git-and-distribution.md` — configure workflow, direct local/Git pack sources, `codepotg.lock.yaml`, CLI, and distributions.
- `07-testing-packs-and-release.md` — official adapters/packs, fixtures, re-authoring, quality gates, and release.
- `08-path-expressions-and-naming.md` — semantic names, `(expression)`, `{selectionKey}`, `{root}`, filesystem compilation, and path conformance.
- `PARALLEL_WORK.md` — active ownership and lane coordination.
- `PROGRESS.md` — append-only evidence log.

Standalone planning fixtures live under [`../examples`](../examples/README.md) and must become schema/conformance fixtures during implementation.

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
