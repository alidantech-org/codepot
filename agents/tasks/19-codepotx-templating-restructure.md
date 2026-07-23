# Task 19 — Templating modularization

Status: [~]
Issue: #17 open
Depends on: Task 18 implementation complete; combined Tasks 17-20 validation pending
Commits: implementation checkpoint from `8be68d2987fde20a1624c9e2f6639ca3dd731c14` through `a81afbc6fce720b35d21ac4559203a6235677c55`; ownership and metadata follow-ups through `a339d2216b37e89d88f9764489d1d1d76a3f9538`
Validation: configuration, compilation, context, variables, references, paths, rendering, and facade modules are committed. Existing behavior and package compatibility await the combined validation gate.

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

- [x] Extract `paths.yaml` input contracts and compatibility-key normalization.
- [x] Extract template source discovery and ignore/hidden-file behavior.
- [x] Extract partial detection and naming.
- [x] Extract folder recipe compilation.
- [x] Extract output path token compilation and validation ownership.
- [x] Extract lifecycle and write-policy compilation.
- [x] Extract template and raw-file descriptor compilation.
- [x] Extract helper validation and template-reference collection ownership.
- [x] Extract compiled template-pack validation.
- [x] Extract deterministic artifact assembly and digesting.
- [x] Adopt `CODEPOT_ARTIFACT_PRODUCER` in template-pack and template-variable artifacts without changing serialized producer values.
- [x] Split context construction from template compilation.
- [x] Split variable catalog creation, formatting, and strict validation into variable use cases and owned modules.
- [x] Split Handlebars renderer construction, partial registration, and virtual-file rendering.
- [x] Keep `DefaultTemplatingEngine` as a small application facade behind the same port.

## Compatibility requirements

- [x] Preserve camelCase and supported legacy snake_case `paths.yaml` keys in raw-to-normalized configuration.
- [ ] Confirm hidden file, raw file, ignore, partial, helper, lifecycle, compare-mode, and output-token behavior under the full suite.
- [x] Preserve strict Handlebars compile/runtime security options in the rendering module.
- [ ] Confirm template context shape and variable catalog output against baseline fixtures.
- [ ] Confirm deterministic template ordering and content digests against baseline fixtures.
- [ ] Confirm representative CodepotG parity where it remains the accepted reference.

## Type-safety requirements

- [x] Define explicit normalized configuration types separate from raw YAML input types.
- [x] Keep raw dictionary access inside typed normalization and compiler boundaries.
- [x] Keep Handlebars runtime objects out of public contracts and stable artifacts.
- [x] Templating imports no authoring implementation modules.

## Acceptance criteria

- [x] Compilation and rendering are separate application operations.
- [x] Template context and variable introspection are separate from filesystem mutation.
- [ ] Compiled template artifacts and rendered virtual files match baseline fixtures.
- [ ] Public `codepotx/templating` exports remain compatible and explicit under package validation.
- [ ] Architecture and package checks pass.

## Validation

```bash
pnpm --filter codepotx typecheck
pnpm --filter codepotx test
pnpm --filter codepotx build
pnpm --filter codepotx package:lint
```
