# Task 19 — Templating modularization

Status: [ ]
Issue: open when ready
Depends on: Task 18
Commit: pending
Validation: pending

## Goal

Separate template-pack loading, configuration normalization, file discovery, compilation, validation, context construction, variable introspection, reference analysis, path handling, and rendering into focused modules while preserving `paths.yaml` and Handlebars behavior.

## Target structure

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
└── index.ts
```

## Work

- [ ] Extract `paths.yaml` input contracts and compatibility-key normalization.
- [ ] Extract template source discovery and ignore/hidden-file behavior.
- [ ] Extract partial detection and naming.
- [ ] Extract folder recipe compilation.
- [ ] Extract output path token compilation and validation.
- [ ] Extract lifecycle and write-policy compilation.
- [ ] Extract template and raw-file descriptor compilation.
- [ ] Extract helper validation and template-reference collection.
- [ ] Extract compiled template-pack validation.
- [ ] Extract deterministic artifact assembly and digesting.
- [ ] Adopt `CODEPOT_ARTIFACT_PRODUCER` from `src/internal/package-info.ts` in template-pack and template-variable artifact assembly without changing serialized producer values.
- [ ] Split context construction from template compilation.
- [ ] Split variable catalog creation, formatting, and strict validation.
- [ ] Split Handlebars renderer construction, partial registration, and virtual-file rendering.
- [ ] Keep `DefaultTemplatingEngine` as a small application facade or replace it with focused use-case composition behind the same port.

## Compatibility requirements

- [ ] Preserve camelCase and supported legacy snake_case `paths.yaml` keys.
- [ ] Preserve hidden file, raw file, ignore, partial, helper, lifecycle, compare-mode, and output-token behavior.
- [ ] Preserve strict Handlebars security options.
- [ ] Preserve template context shape and variable catalog output.
- [ ] Preserve deterministic template ordering and content digests.
- [ ] Compare representative behavior against CodepotG where it remains the accepted reference.

## Type-safety requirements

- [ ] Define explicit normalized configuration types separate from raw YAML input types.
- [ ] Avoid untyped dictionary access when a discriminated configuration type can be used.
- [ ] Keep Handlebars runtime objects out of public contracts and stable artifacts.
- [ ] Do not allow templating to import authoring implementation modules.

## Acceptance criteria

- [ ] Compilation and rendering can be tested independently.
- [ ] Template context and variable introspection can be tested without filesystem mutation.
- [ ] Compiled template artifacts and rendered virtual files match baseline fixtures.
- [ ] Public `codepotx/templating` exports remain compatible and explicit.
- [ ] Architecture and package checks pass.

## Validation

```bash
pnpm --filter codepotx typecheck
pnpm --filter codepotx test
pnpm --filter codepotx build
pnpm --filter codepotx package:lint
```
