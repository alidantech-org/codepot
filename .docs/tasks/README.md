# Codepot task system

This directory is the canonical control plane for planned and active work. Architecture documents define what the system means; tasks define a bounded change, ownership, dependencies, acceptance criteria, and proof.

## Task states

- `draft` — requirement exists but is incomplete.
- `planned` — architecture and dependencies are understood, but execution details may remain.
- `ready` — fully implementable with no unresolved material decision.
- `claimed` — assigned to one active owner.
- `in_progress` — implementation has started.
- `blocked` — cannot continue without a dependency or decision.
- `review` — implementation is complete and evidence is being checked.
- `complete` — acceptance criteria and required evidence are confirmed.
- `superseded` — replaced by a newer task or decision.

A checkbox never substitutes for task state and evidence.

## Required task fields

Every implementation task must identify:

- ID and title;
- status, priority, owner, package or app, and subsystem;
- dependencies and conflicts;
- required reading;
- allowed and forbidden paths;
- problem and evidence;
- scope and non-goals;
- architecture constraints;
- expected behavior;
- acceptance criteria;
- exact tests and manual proof;
- documentation and release impact;
- completion evidence and handoff.

## Execution gate

An AI may implement only a `ready` task that is explicitly assigned or approved, has complete dependencies, and does not overlap another active owner.

## Organization

- [`dryv/`](dryv/README.md) — active Dryv package-family work.
- [`apps/`](apps/README.md) — documentation and site applications.
- [`cross-cutting/`](cross-cutting/README.md) — repository-wide work spanning components.
- [`templates/`](templates/README.md) — task, program, architecture proposal, and handoff templates.
- [`INDEX.md`](INDEX.md) — current program and task registry.

Tasks stay at stable paths when status changes. Do not move them between `todo`, `doing`, and `done` folders.
