---
title: Repository structure
description: Where applications, packages, documentation, and historical material belong.
---

# Repository structure

```text
apps/                         executable applications
packages/<ecosystem>/         reusable packages grouped by ecosystem
.docs/                        all canonical authored documentation
.archives/                    historical, read-only material
README.md                     human entry point
AGENTS.md                     AI router and safety gate
```

## Documentation ownership

Applications and packages keep one concise root `README.md`. Architecture, tasks, plans, audits, operations, public documentation, and AI instructions live under `.docs`.

## Status ownership

The canonical component registry is `.docs/project/component-status.md`. A directory's presence does not make it active.

## Repository safety

- Work on `develop`.
- Do not create branches.
- Do not edit `.archives/**`.
- Do not modify frozen packages without an explicit maintenance task.
- Do not add random root files or new top-level directories.
- Do not hide architecture changes inside implementation work.
