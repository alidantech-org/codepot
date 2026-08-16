# HELPER-01 — Dryv Author architecture cleanup

Status: TODO
Prerequisites: approved `TASKS.md`; current Dryv Canonical IR inspected.

## Goal
Replace the current helper layout with the approved folder-based Author ownership model without carrying forward obsolete architecture.

## Required result
Create/reshape the production package around `api/`, `core/`, `features/`, `compiler/`, `validation/`, `loading/`, and `host/`. Under `features/`, establish the required real owners for properties, schemas, operations, failures, events, workflows, storage, policies, views, presentations, sources, and groups. Under `compiler/`, establish context, naming, resolvers and passes.

This task may move/rewrite useful current code, but old files are not compatibility contracts. Remove stale flat owners and placeholder trees once their concepts have a final owner.

## Enforcement
- No tests or test execution.
- No compatibility aliases/shims or legacy exports.
- No application code generation, templates, pack selection, output paths, or filesystem writing in Author.
- No empty speculative plugin/adapters architecture.
- `__init__.py` files expose intentional public surfaces only.
- Source files target <=500 lines.

## Completion
- Final package ownership matches `TASKS.md`.
- Every retained current concept has one clear owner.
- Superseded production files are physically removed, not deprecated.
- No removed `dryv`/legacy Author concepts remain imported merely to preserve old behavior.

Do not implement later feature semantics opportunistically beyond what is needed to establish clean boundaries.