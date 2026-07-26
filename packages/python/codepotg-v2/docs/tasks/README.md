# Task tracking

Task files use ordinary Markdown checkboxes:

- `[ ]` — not started;
- `[x]` — completed;
- add `**IN PROGRESS**` after an unchecked task when active;
- add a short indented note with the commit SHA, test command, decision, or blocker.

Every implementation commit must update the relevant checklist and append a row to `PROGRESS.md`. Tasks are marked complete only when implementation, focused tests, documentation, and architectural validation are all complete.

The master sequence is in [`00-master-plan.md`](00-master-plan.md). Package-specific adapters and packs have independent task ledgers in their own `docs/tasks` folders.
