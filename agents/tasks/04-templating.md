# Phase 04 — Templating and Handlebars migration

Status: [ ]
Issue: open when stable artifacts and platform ports are ready
Depends on: Phases 01 and required Phase 02 services
Commit: pending
Validation: pending

## Goal

Port the important `codepotg` template-pack behavior to a standalone Handlebars templating engine that consumes only stable authoring artifacts.

## 04.1 Template-pack contracts

- [ ] Define template-pack config, compiled pack, template descriptor, context, dependency, import, and render contracts before implementation.
- [ ] Keep template-specific metadata outside authoring artifacts.
- [ ] Version stable template contexts deliberately.

## 04.2 `paths.yaml`

- [ ] Port loading, defaults, and validation.
- [ ] Port folder recipes, aliases, `each`/`group`/`once` selection, and lifecycle overrides.
- [ ] Port dynamic path expressions and escaped bracket/brace tokens.
- [ ] Port template-extension stripping, static files, and raw-file permission.
- [ ] Port managed, immutable, protected, and clean-root policies.

## 04.3 Context and planning support

- [ ] Compile global context from `CompiledAuthoringArtifact`.
- [ ] Expand per-folder and per-file contexts deterministically.
- [ ] Provide current-file metadata.
- [ ] Resolve dependencies, inheritance, self-dependencies, missing targets, and importability.
- [ ] Build output indexes and language-aware import/link planning through injected strategies.

## 04.4 Handlebars

- [ ] Implement template scanning and static-file discovery.
- [ ] Implement Handlebars environment, helpers, partials, strict missing-value diagnostics, and safe extension handling.
- [ ] Render virtual files without writing.
- [ ] Preserve deterministic ordering and source-aware diagnostics.

## 04.5 Validation

- [ ] Compare path expansion against Python fixtures.
- [ ] Compare selected contexts, dependencies, imports, and planned paths.
- [ ] Compare converted Jinja fixtures with Handlebars expected output.
- [ ] Verify static/raw files and lifecycle policies.
- [ ] Run entirely with memory adapters.
- [ ] Typecheck, tests, build, and package validation pass.
- [ ] Record issue, commit, and evidence before marking complete.
