# AI contributor system

This directory is the canonical operating manual for AI agents working in Codepot.

The root [`AGENTS.md`](../../AGENTS.md) is only a router and safety gate. Detailed rules, guides, and reusable skills live here.

## Mandatory reading order

Before changing any file:

1. Read root [`AGENTS.md`](../../AGENTS.md).
2. Read [`../project/component-status.md`](../project/component-status.md).
3. Read [`rules/repository.md`](rules/repository.md).
4. Read [`rules/architecture.md`](rules/architecture.md).
5. Read the assigned task under [`../tasks`](../tasks/README.md).
6. Read the relevant architecture and product documents named by the task.
7. Select and follow the appropriate skill under [`skills/`](skills/README.md).

## Sections

- [`rules/`](rules/README.md) — non-negotiable repository, architecture, documentation, task, and verification rules.
- [`guides/`](guides/README.md) — explanatory workflows for inspecting, planning, implementing, reviewing, and handing off work.
- [`skills/`](skills/README.md) — concise repeatable procedures an agent can execute.

## Rule hierarchy

1. Explicit user instructions for the current task.
2. Root `AGENTS.md` and `.docs/agents/rules`.
3. Approved architecture under `.docs/architecture`.
4. The assigned task contract.
5. Product and application documentation.
6. Existing implementation patterns.

An agent must not use stale code, old documentation, or archived material to override a higher authority.
