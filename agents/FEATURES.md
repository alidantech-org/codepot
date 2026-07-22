# Codepot required features

## Authoring

- `codepotx.config.ts` as the canonical entrypoint.
- `defineCodepotConfig` as the canonical config helper.
- complete compatibility with the old TypeScript authoring DSL and compiler meaning.
- Codepot-owned `schema` namespace and `z` compatibility namespace.
- internal Zod metadata extraction without a peer dependency.
- consumer `tsconfig.json` and path-alias support.
- loading only the reachable authoring module graph rather than building the whole application.
- validation, structured diagnostics, stable debug output, caching, and artifact mode.
- deterministic `CompiledAuthoringArtifact` generation without requiring OpenAPI.

## Templating

- `paths.yaml` loading and validation.
- Handlebars templates and partials.
- static/raw files.
- folder selectors, aliases, selection modes, and dynamic path expressions.
- escaped path tokens.
- stable global and per-file template contexts.
- dependency resolution and import planning.
- managed, immutable, protected, and clean lifecycle rules.
- deterministic `CompiledTemplatePack` and render diagnostics.

## Generation

- `CodepotFile.yml` and optional `.yaml` compatibility.
- explicit `allow: true` execution permission.
- defaults, named tasks, single-task selection, and all-task execution.
- local, package, Git, and precompiled artifact sources.
- before/after commands with cwd, environment, optional failures, output capture, and dry-run behavior.
- safe cleanup with root, protected, immutable, and clean-path enforcement.
- deterministic planning before rendering.
- in-memory virtual files before writing.
- changed-aware, atomic writing with exact, layout-insensitive, and binary comparison.
- created, updated, unchanged, skipped, immutable, refused, cleaned, and command results.

## Runtime

- explicit dependency injection and dependency inversion.
- default Node adapters and in-memory test adapters.
- typed request/result dispatch.
- cancellation through `AbortSignal`.
- per-run context and correlation.
- typed event subscriptions for progress, diagnostics, tracing, file lifecycle, and command lifecycle.
- stable feature and capability discovery.
- no CLI coupling.

## Frontends

- external CLI package as the first frontend.
- runtime API usable by IDE extensions, desktop/local web clients, tests, and other Node programs.
- identical requests, results, diagnostics, and events across frontends.

## Compatibility and quality

- old contract fixtures compile with import-only migration.
- Python `codepotg` generation behavior is deliberately ported, not casually rewritten.
- stable artifact and template-context versioning.
- deterministic snapshots and end-to-end fixtures.
- package validation, clean exports, no deep internal public paths, and no `.js` suffixes in authored TypeScript imports.
