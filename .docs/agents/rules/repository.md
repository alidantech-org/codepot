# Repository working rules

## Branch and Git

- Work only on the existing `develop` branch.
- Never create a branch.
- Never push to another branch.
- Do not modify `.github/**` without explicit user approval.
- Do not rewrite unrelated history or discard unrelated user changes.

## Component status

- Active work is limited to components marked active in [`../../project/component-status.md`](../../project/component-status.md).
- Frozen packages may change only through a ready task that explicitly names the package and maintenance scope.
- `.archives/**` is read-only. Do not edit it, import from it, or copy an archived implementation as a shortcut.

## Scope

- Inspect before editing.
- Change only paths permitted by the assigned task.
- Do not perform broad cleanup, dependency upgrades, renames, or redesign while completing a focused task.
- Do not add new top-level folders without an approved repository-structure change.
- Keep temporary files, generated output, caches, and local environments out of commits.

## File placement

- Executable applications belong under `apps/`.
- Reusable packages belong under `packages/<ecosystem>/`.
- Canonical documentation belongs under `.docs/`.
- Apps and packages keep only a concise root README as authored project documentation.
