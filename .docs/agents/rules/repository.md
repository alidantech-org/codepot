# Repository working rules

## Branch and Git

- Work only on the existing `develop` branch.
- Never create or push another branch.
- Do not modify `.github/**` without explicit user approval.
- Do not rewrite unrelated history or discard unrelated user changes.

## Component status

Active:

- `apps/docs`
- `apps/site`
- `packages/python/dryv`
- `packages/python/dryv-author`
- `packages/python/dryv-cli`
- `packages/python/dryv-template-jinja`
- `packages/python/dryv-language-typescript`
- `packages/python/dryv-language-dart`

Frozen:

- `packages/python/codepotg`
- `packages/nodejs/codepot-openapi`
- `packages/nodejs/codepotx`
- `packages/nodejs/codepotx-cli`

Frozen packages have no active tasks or backlog. Modify one only after an explicit user instruction authorizes narrow maintenance.

`.archives/**` is historical and read-only except during an explicitly approved archive migration. Never import from it or copy archived implementation as a shortcut.

## Scope

- Inspect before editing.
- Change only the current package, app, or explicitly approved documentation migration paths.
- Do not expand focused work into unrelated cleanup, dependency upgrades, or redesign.
- Keep temporary files, generated output, caches, and local environments out of commits.

## Python workspace

All packages under `packages/python/` use the root `uv` workspace.

```bash
uv sync --all-packages
uv run --all-packages pytest
uv run ruff check packages/python
```

Use `uv sync`, `uv run`, `uv add`, `uv lock`, and `uv build`. Do not use package-local virtual environments, `pip install`, editable installs, `PYTHONPATH`, pytest `pythonpath`, or independently managed requirements files to connect workspace packages.

## File placement

- Executable applications belong under `apps/`.
- Reusable packages belong under `packages/<ecosystem>/`.
- Active internal documentation mirrors those paths under `.docs/apps/` and `.docs/packages/`.
- Package and app roots keep only concise README entry points.
