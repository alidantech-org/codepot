# Task 25 — CodepotG complete template-variable contract

Status: [-]
Branch: `chatgpt/codepotx-restart`
Depends on: Task 24 JSONL/lazy generation foundation and the 356-test realistic-pack checkpoint

## Goal

Expose every supported OpenAPI and `x-codegen` fact through stable typed template contracts while preserving complete lossless access through `api.raw`, `api.extensions`, and per-item `meta` escape hatches. Prove each public variable from real Jinja templates rather than Python-only assertions.

## Required work

- [-] Inventory every public root documented under `packages/python/codepotg/docs`.
- [x] Keep `project`, `api`, `lang`, `emit`, `resources`, `schemas`, `operations`, `entities`, `frontends`, selected frontend roots, `file`, and `meta` stable.
- [x] Ensure bounded graph contexts expose `normalized`, `domains`, `schema_contract`, `codegen_contract`, `entity_contract`, and `frontend_contract` only where declared.
- [x] Add and expose the typed lossless top-level `document_contract` root.
- [x] Preserve all authored top-level OpenAPI source information in typed facts or lossless raw/extension escape hatches.
- [-] Preserve every selected-item source value through typed facts or per-item raw/extension/meta escape hatches.
- [x] Attach normalized contracts once at the inference boundary and reuse them in bounded rendering.
- [x] Expose the same normalized roots through direct eager, queued legacy, and bounded graph rendering without leaking hidden graph selections.
- [x] Add typed context aliases instead of loose undocumented dictionaries for the planned bounded roots.
- [-] Add Jinja text fixtures that render every global and selected-item variable family.
- [-] Test schema, resource, operation, entity, frontend, parameter, request, response, field, file, dependency, provider, barrel, and lazy-source contexts.
- [x] Test missing top-level optional data produces safe empty values rather than undefined-template failures.
- [ ] Test safe empty values for every selected-item contract family.
- [ ] Update the variable reference and bounded-context documentation from executable tests.

## Implemented evidence awaiting validation

- `normalized_document_contract.py` covers info, servers, paths, webhooks, all reusable component registries, security, tags, external docs, extensions, raw source, diagnostics, and loss counts.
- Lossless inference stores the shared object at `api.meta["normalized_document"]`.
- Bounded graph contexts reuse that object as `document_contract` while keeping the full compatibility `api` root hidden for selection resolution only.
- The renderer injects the same precomputed document and normalized roots into eager/legacy contexts only when the public `api` root is present; bounded contexts without `api` are not augmented.
- Contract and renderer tests verify all standard top-level OpenAPI families, raw-only preservation, extensions, safe missing values, object identity, eager fallback construction, and bounded no-leak behavior.
- The complete graph fixture now renders fields, dependencies, imports, parameters, request bodies, responses, providers, provider outputs, barrels, resolver statistics, and lazy source records into inspectable text files.
- Portable-language Jinja fixtures prove global, schema, operation, resource, raw, extension, file-writing, package-layout, and cache-reuse behavior; entity/frontend and safe-empty selected-item probes remain open.

## Safety constraints

- Do not remove existing variables or compatibility aliases.
- Do not load the full normalized document into bounded graph contexts.
- Do not weaken write-policy, dependency-provider, collision, or path traversal validation.
- Keep raw source access an explicit escape hatch; templates should prefer typed normalized facts.

## Validation

- [ ] Ruff passes.
- [ ] Variable-contract fixture tests pass.
- [ ] Existing realistic Nest, Next, and Dart packs remain passing.
- [ ] Complete package suite passes.
