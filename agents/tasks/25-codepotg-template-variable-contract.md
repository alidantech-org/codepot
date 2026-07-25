# Task 25 — CodepotG complete template-variable contract

Status: [-]
Branch: `chatgpt/codepotx-restart`
Depends on: Task 24 JSONL/lazy generation foundation and the 356-test realistic-pack checkpoint

## Goal

Expose every supported OpenAPI and `x-codegen` fact through stable typed template contracts while preserving complete lossless access through `api.raw`, `api.extensions`, and per-item `meta` escape hatches. Prove each public variable from real Jinja templates rather than Python-only assertions.

## Required work

- [ ] Inventory every public root documented under `packages/python/codepotg/docs`.
- [ ] Keep `project`, `api`, `lang`, `emit`, `resources`, `schemas`, `operations`, `entities`, `frontends`, selected frontend roots, `file`, and `meta` stable.
- [ ] Ensure bounded graph contexts expose `normalized`, `domains`, `schema_contract`, `codegen_contract`, `entity_contract`, and `frontend_contract` only where declared.
- [ ] Preserve all authored source information in typed facts or lossless raw/extension/meta escape hatches.
- [ ] Add typed context aliases instead of loose undocumented dictionaries where a planned public root is missing.
- [ ] Add Jinja text fixtures that render every global and selected-item variable family.
- [ ] Test schema, resource, operation, entity, frontend, parameter, request, response, field, file, dependency, provider, barrel, and lazy-source contexts.
- [ ] Test missing optional data produces safe empty values rather than undefined-template failures.
- [ ] Update the variable reference and bounded-context documentation from executable tests.

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
