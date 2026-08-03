# Phase 04 — Templating and Handlebars migration

Status: [x]
Issue: #6
Depends on: Stable artifacts and platform ports
Commits: `877b13228f78a8d6bf408346c29acc4258c94382`, `4296bb730749ff2d12db94b23d93297a7e98874b`
Validation: focused memory-source template pack tests cover `paths.yaml`, snake_case compatibility, `{folder}` groups, `[expression]` paths, strict Handlebars helpers, stable template artifacts, stable context creation, and in-memory virtual-file rendering. Full dependency-installed execution remains part of the Phase 07 package gate.

## Completed

- [x] Implemented `TemplatingPort` through explicit dependency injection.
- [x] Added `paths.yaml` validation and stable `CompiledTemplatePack` output.
- [x] Ported configured folder, dynamic path, lifecycle, write-root, raw-file, and template-extension behavior.
- [x] Added strict Handlebars rendering with explicit helpers.
- [x] Kept rendering in memory and excluded filesystem writes from templating.
- [x] Added `codepotx/templating` package export.
