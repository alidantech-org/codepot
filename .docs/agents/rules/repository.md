# Repository working rules

## Branch and Git

- Work only on the existing `develop` branch.
- Never create or push another branch.
- Do not modify `.github/**` without explicit user approval.
- Do not rewrite unrelated history or discard unrelated user changes.

## Component status

Active current Python architecture work:

- `packages/python/dryv`
- `packages/python/dryv-api`

Deferred/removed client implementations are not active architecture work. Do not recreate Python author, CLI, template-client or language-adapter packages unless the user explicitly starts that independent client work again. Future Project Clients may preferably be implemented in TypeScript.

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
- Do not expand focused work into unrelated cleanup, dependency upgrades or redesign.
- Keep temporary files, generated output, caches and local environments out of commits.
- When a package has a package-specific implementation-rules document, it is mandatory.

## Python workspace

All packages under `packages/python/` use the root `uv` workspace.

Use `uv sync`, `uv run`, `uv add`, `uv lock`, and `uv build` when executable validation is authorized. Do not use package-local virtual environments, `pip install`, editable installs, `PYTHONPATH`, pytest `pythonpath`, or independently managed requirements files to connect workspace packages.

The active Dryv refactor currently forbids creating/modifying tests until explicit user approval; generic workspace test commands do not override that package-specific gate.

## File placement

- Executable applications belong under `apps/`.
- Reusable packages belong under `packages/<ecosystem>/`.
- Active internal documentation mirrors those paths under `.docs/apps/` and `.docs/packages/`.
- Package and app roots keep only concise README entry points.
- Do not create compatibility packages or duplicate package roots to preserve superseded architecture.
