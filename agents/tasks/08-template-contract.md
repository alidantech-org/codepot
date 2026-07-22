# Phase 08 — Template variable contract and validation

Status: [~]
Issue: create before implementation
Depends on: completed authoring and templating engines
Commits: pending
Validation: pending

## Goal

Make every value available to Handlebars explicit, typed, listable, and validatable. Template authors must be able to inspect the complete context contract before writing a template, and Codepot must detect unknown or unavailable variables before rendering.

## Tasks

- [ ] Define stable template-variable catalog contracts in `contract`.
- [ ] Define variable kinds, scopes, availability, examples, descriptions, and source metadata.
- [ ] Add typed requests/results and `TemplatingPort` methods for listing variables and validating contexts.
- [ ] Build the catalog deterministically from `CompiledAuthoringArtifact`, project variables, frontend selection, generation metadata, and per-file context.
- [ ] Parse Handlebars ASTs and collect referenced paths, helpers, partials, block parameters, and data variables.
- [ ] Validate referenced paths against the catalog before generation.
- [ ] Validate `paths.yaml` selectors and dynamic path expressions against the same catalog.
- [ ] Add `codepotx variables` and runtime operations for machine-readable and human-readable output.
- [ ] Generate JSON and Markdown catalog formats for documentation tools.
- [ ] Add focused tests for listing, validation, aliases, arrays, optional values, partials, helpers, and path expressions.

## Rules

- The catalog is a stable serializable artifact; it contains no Zod or Handlebars runtime objects.
- Template validation must never execute user templates.
- Unknown variables are errors; optional variables are represented explicitly.
- Helpers, partials, and `@data` variables are separate namespaces.
- Templating may consume only stable authoring artifacts and injected platform services.
