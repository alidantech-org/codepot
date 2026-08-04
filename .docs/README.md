# Codepot documentation

`.docs` is the canonical home for repository documentation.

- [`WHY.md`](WHY.md) explains why Codepot exists.
- [`TODO.md`](TODO.md) points to the small amount of work currently in focus.
- [`agents/`](agents/README.md) contains the detailed rules, guides, and skills for AI contributors.
- `packages/<ecosystem>/<package>/` mirrors package paths and owns each package's active internal documentation.
- `apps/<app>/` mirrors application paths and owns each app's active internal documentation.
- [`public/`](public/README.md) contains documentation approved for publication.

Each package or app has exactly one active internal documentation folder. Other documents link to that folder instead of repeating its architecture, status, or task information.

A detailed task, when one exists, lives under its owning item. `TODO.md` only points to the current item and goal. Completed, abandoned, frozen, and superseded material moves to `.archives/.docs` after durable facts are incorporated into current documentation.

Dryv currently has no active implementation tasks while its next plan is being derived. Its package documentation records implemented architecture and the cleanup, rewrite, and improvement direction only.
