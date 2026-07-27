# Task dependencies and safe parallelism

## Branch naming

GitHub cannot create a branch nested below the existing `chatgpt/codepotx-restart` ref. Use one slash and hyphenated suffixes:

```text
chatgpt/codepotx-restart-codepotg-author
```

Do not use:

```text
chatgpt/codepotx-restart/codepotg-author
```

## Main implementation sequence

```text
Batch A: AUTHOR-001..AUTHOR-008
package, options, session, diagnostics, IDs, refs, typing

Batch B: AUTHOR-009..AUTHOR-013
properties, schemas, Pydantic, field selectors, projections

Batch C: AUTHOR-015..AUTHOR-020
storage, policies, events, operations, current HTTP, triggers/execution

Batch D: AUTHOR-022, AUTHOR-024, AUTHOR-027
views, workflows, multi-pass compiler and core validation

Batch E: AUTHOR-028
canonical JSON/YAML transport and strict round trip

Batch F: AUTHOR-029..AUTHOR-030
connected fixtures, performance, distribution, docs/release
```

## Core-evolution lane

These tasks cannot be completed privately by the author package:

```text
AUTHOR-014 field capability facets
AUTHOR-019 extended HTTP bindings beyond current public facet
AUTHOR-021 value sources
AUTHOR-023 presentations
AUTHOR-025 tags
AUTHOR-026 guidance
AUTHOR-028 public codec ownership when core must expose it
```

A separate approved core lane must publish typed models, validation, selectors, template contexts, fixtures, compatibility rules, and behavior/IR version changes. The author agent records blockers and continues independent batches.

## File ownership

Author implementation owns only:

```text
packages/python/codepotg-author/**
```

Package coordination may update:

```text
packages/python/codepotg-v2/docs/tasks/PARALLEL_WORK.md
```

It must not modify:

```text
packages/python/codepotg-v2/src/codepotg/**
other adapter/package implementation directories
.github/**
```

## Synchronization

After every one or two coherent commits:

```bash
git fetch origin
git log --oneline HEAD..origin/chatgpt/codepotx-restart
```

When base advanced:

```bash
git merge --no-edit origin/chatgpt/codepotx-restart
```

Do not rebase a published feature branch. Do not force-push. Resolve shared task-ledger conflicts by preserving every lane.

## Commit batches

Recommended commits:

```text
feat(codepotg-author): add author session and typed refs
feat(codepotg-author): add property and schema authoring
feat(codepotg-author): add Pydantic model compiler and projections
feat(codepotg-author): add storage policy event and operation authoring
feat(codepotg-author): add view workflow and compiler passes
test(codepotg-author): add typing architecture and connected coverage
feat(codepotg-author): add canonical IR JSON YAML transport
test(codepotg-author): add distribution performance and round-trip gates
docs(codepotg-author): record support blockers and evidence
```

## Parallel sub-agents

One lead agent must own public API shapes and ref/compiler context. Sub-agents may work after those contracts are committed:

- transport codec/tests;
- Pydantic interpretation fixtures;
- architecture/typing tests;
- documentation/examples;
- benchmarks/distribution.

Sub-agents must not independently invent public builders, ref kinds, IDs, diagnostics, or compiler pass contracts.
