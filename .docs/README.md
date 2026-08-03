# Codepot documentation

This directory is the single canonical home for authored Codepot documentation.

Code lives with the application or package that executes it. Architecture, plans, tasks, research, agent instructions, audits, operational guides, and public documentation live here. Applications and packages keep only a concise local `README.md` that explains the component and links back to this directory.

## Documentation map

- [`project/`](project/README.md) — project identity, repository structure, component status, and development model.
- [`architecture/`](architecture/README.md) — approved Codepot and Dryv architecture.
- [`products/`](products/README.md) — active Dryv product documentation and frozen package records.
- [`apps/`](apps/README.md) — documentation for active applications.
- [`agents/`](agents/README.md) — rules, guides, and reusable skills for AI contributors.
- [`tasks/`](tasks/README.md) — canonical task planning, ownership, status, and evidence.
- [`decisions/`](decisions/README.md) — approved architecture decision records.
- [`audits/`](audits/README.md) — technical audits and review evidence.
- [`examples/`](examples/README.md) — documentation-owned examples and design fixtures.
- [`operations/`](operations/README.md) — release, publishing, and deployment guidance.
- [`public/`](public/README.md) — Markdown and navigation consumed by the documentation site.
- [`plan/`](plan/README.md) — existing implementation planning documents; intentionally unchanged in this reorganization.
- [`research/`](research/README.md) — existing research and engineering papers; intentionally unchanged in this reorganization.

## Authority rule

A document has one canonical owner. Do not duplicate the same rule or design in an application, package, task, or agent file. Link to the canonical document instead.

When documentation and implementation disagree, do not silently choose one. Record the discrepancy in a task or architecture proposal and resolve it explicitly.
