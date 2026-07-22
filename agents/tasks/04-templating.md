# Phase 04 — Templating and Handlebars migration

Status: [x]
Issue: #6
Depends on: Stable artifacts and platform ports
Commit: pending
Validation: focused memory-source template pack tests cover `paths.yaml`, snake_case compatibility, `{folder}` groups, `[expression]` paths, strict Handlebars helpers, stable template artifacts, stable context creation, and in-memory virtual-file rendering.

## Completed

- [x] Implemented `TemplatingPort` through explicit dependency injection.
- [x] Added `paths.yaml` validation and stable `CompiledTemplatePack` output.
- [x] Ported configured folder, dynamic path, lifecycle, write-root, raw-file, and template-extension behavior.
- [x] Added strict Handlebars rendering with explicit helpers.
- [x] Kept rendering in memory and excluded filesystem writes from templating.
- [x] Added `codepotx/templating` package export.
