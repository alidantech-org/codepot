# Phase 06 — External CLI frontend

Status: [x]
Issue: #8
Depends on: Stable runtime generation flow
Commits: pending
Validation: focused CLI tests cover argument parsing and direct typed runtime request mapping. The CLI dynamically prefers the project-local `codepotx/runtime` export and falls back to its declared compatible dependency.

## Completed

- [x] Added the default dependency-injected runtime composition factory.
- [x] Added a separate `codepotx-cli` workspace package and `codepotx` binary.
- [x] Added generate, plan, validate, inspect, features, help, and version commands.
- [x] Added JSON, verbose event, task, project root, dry-run, refresh, and command-skip options.
- [x] Kept domain logic out of the CLI.
- [x] Added deterministic exit codes and diagnostic presentation.
