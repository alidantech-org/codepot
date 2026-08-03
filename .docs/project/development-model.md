# Development model

- Work only on the existing `develop` branch.
- Never create a branch unless the user explicitly changes this rule.
- Do not modify `.github/**` without explicit approval.
- Implementation work must be backed by a task under `.docs/tasks`.
- An AI may implement only a task that is ready, assigned, dependency-safe, and explicit about allowed paths and acceptance criteria.
- Architecture changes require an approved proposal before implementation.
- Preserve unrelated user changes and avoid broad cleanup inside focused tasks.
- Record exact validation commands and results. Never write only “tests passed.”
- One active owner may edit a task’s implementation lane at a time.
- Prefer one coherent concern per commit.
