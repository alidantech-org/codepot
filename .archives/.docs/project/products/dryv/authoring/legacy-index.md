# dryv-author documentation

This documentation locks the design of the typed Python authoring compiler before runtime implementation begins.

## Reading order

1. [`IDEA.md`](IDEA.md) — approved product direction and complete authoring model.
2. [`design/00-authoring-architecture.md`](design/00-authoring-architecture.md) — ownership and package boundaries.
3. [`design/01-refs-and-typing.md`](design/01-refs-and-typing.md) — typed refs, usage wrappers, forward refs, and static/runtime checks.
4. [`design/02-connected-schemas-and-fields.md`](design/02-connected-schemas-and-fields.md) — reusable properties, schema composition, field capabilities, storage-relative behavior, and derivation.
5. [`design/03-operations-facets-effects-and-sources.md`](design/03-operations-facets-effects-and-sources.md) — operation authoring, known facets, effects, value sources, and cross-operation connections.
6. [`design/04-views-presentations-and-guidance.md`](design/04-views-presentations-and-guidance.md) — views, parts, neutral presentations, placement, navigation, and information guidance.
7. [`design/05-tags-and-template-context.md`](design/05-tags-and-template-context.md) — immutable namespaced tags and safe template access.
8. [`design/06-ir-json-yaml-transport.md`](design/06-ir-json-yaml-transport.md) — canonical JSON/YAML serialization, strict round trips, debugging, and shipping.
9. [`design/07-compiler-and-validation.md`](design/07-compiler-and-validation.md) — compiler passes, diagnostics, determinism, and validation.
10. [`design/08-boundaries-and-kernel-gates.md`](design/08-boundaries-and-kernel-gates.md) — non-goals and required intentional core changes.
11. [`tasks/00-master-plan.md`](tasks/00-master-plan.md) — AUTHOR-001 through AUTHOR-030.
12. [`tasks/01-dependencies-and-parallelism.md`](tasks/01-dependencies-and-parallelism.md) — safe parallel batches and merge order.
13. [`prompts/IMPLEMENTATION_PROMPT.md`](prompts/IMPLEMENTATION_PROMPT.md) — complete handoff prompt for another AI.

## Governing invariants

- There is one Codepot semantic IR.
- Authoring is a compiler frontend, not a second graph.
- Author declarations may be concise and composable; compiled IR is explicit and rigid.
- The package may depend on Pydantic; core must not depend on Pydantic.
- Every ref belongs to an explicit author session. No process-global registry exists.
- Authoring objects, Pydantic models, Python callables, and builder state never enter IR or template contexts.
- Tags are immutable namespaced Boolean hints. They never replace typed refs or known semantic fields.
- JSON/YAML documents contain compiled IR, not authoring state.
- Packs and templates interpret neutral semantics; authoring does not model frameworks or runtimes.
- Missing semantic concepts are recorded as core evolution gates, never smuggled through private facets or arbitrary extensions.
