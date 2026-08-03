# Codepot agent instructions

This file is the repository entry point for AI contributors. Detailed rules, guides, and skills live under [`.docs/agents/`](.docs/agents/README.md).

## Mandatory rules

1. Work only on the existing `develop` branch. Never create a branch.
2. Read [`.docs/agents/README.md`](.docs/agents/README.md) before changing files.
3. Read [`.docs/project/component-status.md`](.docs/project/component-status.md) before selecting a component.
4. Implement only a ready, explicitly assigned task under [`.docs/tasks/`](.docs/tasks/README.md).
5. Do not modify frozen packages unless the task explicitly authorizes narrow maintenance.
6. Treat `.archives/**` as read-only. Never import from it or copy it as an implementation shortcut.
7. Keep all canonical authored documentation under `.docs/**`. Apps and packages keep only a concise root `README.md`.
8. Do not modify `.github/**` without explicit user approval.
9. Inspect before editing, remain inside allowed paths, preserve unrelated work, and record exact validation evidence.
10. Do not silently change the semantic kernel, package boundaries, public contracts, generation ownership, or architecture.
11. Manage every package under `packages/python/` through the root `uv` workspace. Do not create or activate package-local virtual environments, use `pip install`, or connect packages through `PYTHONPATH`.

## Required routing

- Repository and documentation rules: [`.docs/agents/rules/`](.docs/agents/rules/README.md)
- Approved architecture: [`.docs/architecture/`](.docs/architecture/README.md)
- Active Dryv product documentation: [`.docs/products/dryv/`](.docs/products/dryv/README.md)
- Application documentation: [`.docs/apps/`](.docs/apps/README.md)
- Python workspace workflow: [`.docs/project/python-workspace.md`](.docs/project/python-workspace.md)
- Task planning and status: [`.docs/tasks/`](.docs/tasks/README.md)
- Repeatable agent procedures: [`.docs/agents/skills/`](.docs/agents/skills/README.md)

When documentation, implementation, and task records disagree, do not guess. Record the contradiction and resolve it through the task or architecture-change process.
