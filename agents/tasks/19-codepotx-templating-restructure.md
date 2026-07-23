# Task 19 — Templating modularization

Status: [x]
Issue: #17 closed
Depends on: Task 18 complete
Commits: implementation checkpoint from `8be68d2987fde20a1624c9e2f6639ca3dd731c14` through `a81afbc6fce720b35d21ac4559203a6235677c55`; ownership and metadata follow-ups through `a339d2216b37e89d88f9764489d1d1d76a3f9538`
Validation: combined Tasks 17–20 gate passed with 45/45 CodepotX tests, strict typechecks, template baseline comparisons, structural checks, build, Publint, and ESM package checks.

## Goal

Separate template-pack loading, raw and normalized configuration, source discovery, descriptor compilation, validation, context construction, variable introspection, reference analysis, path handling, and rendering while preserving accepted `paths.yaml` and Handlebars behavior.

## Completed structure

```text
src/templating/
├── config/
├── compiler/
├── paths/
├── context/
├── rendering/
├── references/
├── variables/
├── application/
└── templating-engine.ts
```

## Completion evidence

- [x] Raw `paths.yaml` input and normalized configuration are separate typed contracts.
- [x] CamelCase and supported legacy snake_case keys remain compatible.
- [x] Discovery preserves ignore, hidden-file, raw-file, partial, and deterministic ordering behavior.
- [x] Folder recipes, path tokens, lifecycle/write policies, template descriptors, helper validation, references, and compiled-pack validation are focused modules.
- [x] Template-pack and template-variable artifacts use centralized producer metadata and preserve digests.
- [x] Context construction, variable catalog formatting, strict context validation, and secure rendering are independent operations.
- [x] Strict Handlebars helper, prototype, and missing-helper security behavior is preserved.
- [x] `DefaultTemplatingEngine` is a small facade over application use cases.
- [x] Context shape, variable catalog, output paths, raw and rendered files, and template artifacts match the baseline suite.
- [x] Templating imports no authoring implementation module and keeps Handlebars runtime objects out of public artifacts.
- [x] `codepotx/templating` package resolution and declarations pass.

## Validation

```bash
pnpm --filter codepotx check
```
