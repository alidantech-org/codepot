# Dryv task tracking

This folder is the implementation control plane for the clean rewrite. Design documents define what must exist; task files define exact work, dependencies, acceptance criteria, ownership, and proof.

## Mandatory rules

- Read `../00-governance/00-approved-architecture.md` and `../00-governance/04-closed-semantic-kernel.md` before claiming work.
- Read `../02-configuration/02-pack-manifest-specification.md` before changing pack configuration.
- Read `../03-generation/00-path-expressions-and-name-tokens.md` before changing discovery, selectors, paths, names, generated dependencies, or official packs.
- Read `../05-distribution/02-git-github-locking-and-trust.md` before changing local/Git providers or locks.
- V2 tasks must not add old `tasks`, project-level `language`, `templateDir`, `paths.yaml`, `registries`, `use`, old runtime imports, or fallback execution.
- The semantic kernel is closed. Adapters, packs, plugins, and templates cannot add semantic objects, relations, facets, selectors, expression roots, context properties, or validation rules for invented concepts.
- Do not use `resource`, `model`, `entity`, `frontend`, or `ui` as neutral v2 kernel/selector/context roots.
- Selectors are fixed, versioned, root-first, and normally begin with `groups` or an active `group` context. Do not add arbitrary query/traversal DSLs.
- Every named semantic projection follows `x.name.{casing}.{number}`.
- Do not add `fileName`, `filePath`, `directory`, language class-name, or similar output conveniences to semantic IR.
- Templates, macros, partials, and static files own every emitted character. Language adapters must not render types, literals, imports, exports, comments, validators, decorators, formatting, or framework code.
- Do not restore root pack `paths`, explicit `files`, `filePatterns`, or profile machinery; ordinary content is filesystem-discovered and explicit emissions are registered under `selections`.
- Generated dependencies are declared through selection keys/symbols and resolved through semantic identity/scope. Templates author dependency syntax.
- Generated output hashes/state belong to ownership/generation state, not `dryv.lock.yaml`.
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
- `02-configuration-and-pack-contracts.md` — simplified project/pack schemas, root-first selections, dependency descriptors, bindings, and exact commands.
- `03-ir-selection-and-planning.md` — closed semantic kernel, known facets, workflows/compensation, fixed selectors, artifact/impact graphs, explain, and conservative incremental generation.
- `04-plugin-system-and-conformance.md` — adapter protocols, discovery, runtime registries, closed-kernel enforcement, and non-rendering target adapter suites.
- `05-writers-cache-and-security.md` — transactional writers, ownership/generation state, cache, exact commands, approvals, and manifests.
- `06-configure-cli-git-and-distribution.md` — configure workflow, direct local/Git pack sources, `dryv.lock.yaml`, CLI, and distributions.
- `07-testing-packs-and-release.md` — connected semantic fixtures, official adapters/packs, re-authoring, impact/incremental verification, and release gates.
- `08-path-expressions-and-naming.md` — naming order, `(expression)`, `{selectionKey}`, `{root}`, root-first contexts, filesystem compilation, and path conformance.
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
