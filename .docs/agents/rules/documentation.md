# Documentation rules

## Canonical ownership

Every package or app has one active internal documentation folder that mirrors its code path:

```text
packages/python/dryv       -> .docs/packages/python/dryv
apps/site                  -> .docs/apps/site
```

Do not create a second product, architecture, audit, design, or task tree for the same item. Link to the owning folder instead of copying its content.

## Root files

- `.docs/README.md` defines the documentation map and lifecycle.
- `.docs/WHY.md` records the stable Codepot thesis.
- `.docs/TODO.md` names only the package or app currently in focus, its current goal, and the detailed task when one exists.

`TODO.md` is not a backlog, progress log, or history. It must remain short and change only when the repository's current focus changes.

## Item documentation

An item starts with only `README.md`. Add architecture, usage, validation, decisions, or task files only when real current content requires them. Empty documentation kits and copied legacy plans are forbidden.

Current documentation describes implemented behavior and approved boundaries. Research, proposals, completed work logs, superseded plans, and historical audits do not remain in the active reading path.

## Tasks

Detailed implementation tasks live under the owning item, for example:

```text
.docs/packages/python/dryv-cli/tasks/portable-output.md
.docs/apps/site/tasks/public-docs.md
```

When work finishes, move the task to `.archives/.docs` after incorporating durable facts into current documentation. Remove its pointer from `.docs/TODO.md`.

Dryv has no active implementation task while its next plan is being derived. Do not recreate a Dryv task ledger until a concrete, approved task exists.

## Public documentation

`.docs/public` is the publication source and the only intentional second location for an item name. Public pages summarize released, implemented, and tested behavior; they must not become the authority for internal architecture or task state.

## Archive

Historical documentation lives under `.archives/.docs`, mirroring its former path where practical. Archive migration is the only reason to write there; archived content is otherwise read-only and must never be copied back as a starting point.

## Package-local files

Package and app READMEs stay concise and link to their canonical `.docs` folder. Package-local `docs/` directories, generated files, templates, fixtures, and code samples do not belong in active documentation.
