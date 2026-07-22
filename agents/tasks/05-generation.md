# Phase 05 — Generation and CodepotFile orchestration

Status: [x]
Issue: #7
Depends on: Authoring and templating ports
Commit: pending
Validation: focused memory-only tests cover `CodepotFile.yml`, stable-artifact planning, deterministic selection, in-memory rendering, changed-aware writing, and unsafe clean refusal.

## Completed

- [x] Implemented the complete `GenerationPort` through injected authoring, templating, platform, command, and writer ports.
- [x] Added `CodepotFile.yml` validation, `allow: true`, defaults, task selection, sources, commands, variables, and old Python key compatibility.
- [x] Added deterministic `once`, `each`, and `group` planning.
- [x] Added safe clean planning, dry-run execution, before/after commands, and managed/immutable writes.
- [x] Rendering always completes in memory before optional writes.
- [x] Programmatic planning accepts supplied stable authoring and template artifacts.
- [x] Added `codepotx/generation` package export.
