# Dryv runtime task ledger

This folder preserves the detailed runtime implementation program and its evidence history.

## Governing documents

Read these before claiming runtime work:

- [Approved architecture](../../../architecture/governance/00-approved-architecture.md)
- [Closed semantic kernel](../../../architecture/governance/04-closed-semantic-kernel.md)
- [Project configuration](../../../architecture/configuration/01-project-config-specification.md)
- [Pack manifest](../../../architecture/configuration/02-pack-manifest-specification.md)
- [Path expressions and naming](../../../architecture/generation/00-path-expressions-and-name-tokens.md)
- [Git, locking, and trust](../../../architecture/distribution/02-git-github-locking-and-trust.md)
- [Runtime examples](../../../examples/dryv/runtime/README.md)

## Ledger files

- `00-master-plan.md` — staged program plan.
- `01-core-foundation-and-api.md` — packages, diagnostics, runtime, and Python API.
- `02-configuration-and-pack-contracts.md` — project and pack schemas, bindings, and commands.
- `03-ir-selection-and-planning.md` — semantic kernel, selectors, planning, impact, and incremental behavior.
- `04-plugin-system-and-conformance.md` — plugin contracts and conformance.
- `05-writers-cache-and-security.md` — writers, ownership, cache, security, and approvals.
- `06-configure-cli-git-and-distribution.md` — configuration, CLI, Git sources, locks, and distribution.
- `07-testing-packs-and-release.md` — connected fixtures, official packs, and release gates.
- `08-path-expressions-and-naming.md` — naming and filesystem compilation.
- `ORCHESTRATOR_PLAN.md` — orchestration design history.
- `PARALLEL_WORK.md` — ownership and lane coordination.
- `PROGRESS.md` — append-only implementation evidence.

## Task rule

A checkbox never substitutes for task status and evidence. A task is complete only after implementation, focused tests, architecture or conformance tests, canonical documentation, exact commands and results, and acceptance confirmation are recorded.

New work must also follow the repository-wide [task rules](../../../agents/rules/tasks.md) and [task template](../../templates/task.md).
