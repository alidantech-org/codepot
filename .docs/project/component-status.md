# Component status

Status is explicit. Repository location does not imply active development.

## Active

- `apps/docs` — dedicated documentation application boundary.
- `apps/site` — public Codepot website and current documentation renderer.
- `packages/python/dryv`
- `packages/python/dryv-author`
- `packages/python/dryv-cli`
- `packages/python/dryv-template-jinja`
- `packages/python/dryv-language-typescript`
- `packages/python/dryv-language-dart`

Active components may receive approved feature, architecture, maintenance, documentation, and release tasks.

## Frozen

- `packages/python/codepotg`
- `packages/nodejs/codepot-openapi`
- `packages/nodejs/codepotx`
- `packages/nodejs/codepotx-cli`

Frozen components remain available for existing users and historical comparison. Do not add features, redesign them, modernize dependencies for cleanliness, or make them dependencies of active Dryv internals. A frozen component may change only when an approved task explicitly authorizes narrowly scoped maintenance.

## Archived

Everything under `.archives/**` is historical and read-only. Active code must not import from it, copy it as an implementation shortcut, or modify it during normal work.

## Status vocabulary

- `active` — receives planned development.
- `maintenance` — essential fixes only.
- `frozen` — retained but not actively developed.
- `experimental` — exploration without product commitment.
- `archived` — historical and read-only.
- `retired` — no longer supported and scheduled for removal or already removed.
