# Codepot agent instructions

This file is the repository router for AI contributors. Detailed rules, guides, and skills live under [`.docs/agents/`](.docs/agents/README.md).

## Mandatory rules

1. Work only on the existing `develop` branch. Never create a branch.
2. Read [`.docs/agents/README.md`](.docs/agents/README.md) before changing files.
3. Read [`.docs/TODO.md`](.docs/TODO.md) and the canonical documentation for the named package or app.
4. Implement code only from an explicit, approved task under the owning package or app.
5. Do not modify frozen packages unless explicitly authorized for narrow maintenance.
6. Treat `.archives/**` as read-only except during an explicitly approved archive migration. Never import from it or copy it as an implementation shortcut.
7. Keep canonical internal documentation under the matching `.docs/packages/**` or `.docs/apps/**` path. Package and app READMEs remain concise entry points.
8. Do not modify `.github/**` without explicit user approval.
9. Inspect before editing, preserve unrelated work, and record exact validation evidence.
10. Do not silently change the semantic kernel, package boundaries, public contracts, generation ownership, or architecture.
11. Manage every package under `packages/python/` through the root `uv` workspace. Do not use package-local virtual environments, `pip install`, or `PYTHONPATH` wiring.

## Routing

- Current focus: [`.docs/TODO.md`](.docs/TODO.md)
- Repository purpose: [`.docs/WHY.md`](.docs/WHY.md)
- Agent rules and procedures: [`.docs/agents/`](.docs/agents/README.md)
- Package documentation: [`.docs/packages/`](.docs/packages/)
- Application documentation: [`.docs/apps/`](.docs/apps/README.md)
- Published documentation: [`.docs/public/`](.docs/public/README.md)
- Component status: [`.docs/project/component-status.md`](.docs/project/component-status.md)
- Python workspace workflow: [`.docs/project/python-workspace.md`](.docs/project/python-workspace.md)

When documentation, implementation, and the current task disagree, do not guess. Stop and resolve the contradiction explicitly.
