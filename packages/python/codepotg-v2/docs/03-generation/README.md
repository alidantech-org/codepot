# 03 — Generation, root-first selection, impact, and output safety

Generation is planned from the closed semantic kernel, pack filesystem, fixed root-first selectors, registered selection folders, explicit generated dependencies/symbols, bindings, and adapter path-validation facts. No renderer or writer is called until semantic validation and the complete artifact plan are valid.

## Mandatory documents

1. [`../00-governance/04-closed-semantic-kernel.md`](../00-governance/04-closed-semantic-kernel.md) — known semantic objects/facets, outer-to-inner context order, workflows, compensation, access, events, storage, and views.
2. [`00-path-expressions-and-name-tokens.md`](00-path-expressions-and-name-tokens.md) — `{selectionKey}`, `{root}`, `(expression)`, `((literal))`, naming, and source-path compilation.
3. [`01-template-file-model.md`](01-template-file-model.md) — filesystem discovery, templates, static/binary files, partials, barrels, symbols, and engine/target inference.
4. [`02-selection-folder-patterns-and-static-files.md`](02-selection-folder-patterns-and-static-files.md) — root-first fixed selectors, nested selection folders, semantic dependencies, exports, barrels, aggregates, and static fan-out.
5. [`03-planning-execution-and-transaction.md`](03-planning-execution-and-transaction.md) — semantic/artifact graphs, validation, impact analysis, rendering, transactions, ownership state, cache, and conservative incremental generation.

## Locked generation rules

- `templates/` is the default discovered content root.
- Literal files preserve their pack-relative paths.
- Only `{selectionKey}` folders require manifest registration; `{root}` emits at the pack output root.
- Dynamic path/name values use `(expression)` and literal parentheses use `((value))`.
- Names always use `x.name.{casing}.{number}`.
- Square brackets remain literal for framework routes.
- Semantic records do not expose invented `fileName`, `filePath`, or `directory` values.
- Fixed root-first `.each`/`.all` selectors replace arbitrary pack-authored traversal/query declarations.
- Normal generation starts from groups, for example `groups.operations.each` or `groups.storage.mappings.each`.
- `resource`, `model`, `entity`, `frontend`, and `ui` are not neutral selector/context roots.
- Static and binary files are copied automatically; `_partials` is not emitted.
- Generated dependencies are explicit through `imports`, `exports`, and `symbols` selection keys.
- Core resolves semantic providers and path/module facts; templates author all import/export syntax.
- Barrels are authored templates and may export other barrels.
- The engine suffix is stripped; target suffixes remain.
- Every semantic reference, destination, dependency, symbol, command, approval, collision, and impact relation is planned before rendering.
- Generated output hashes belong to ownership/generation state, not `codepotg.lock.yaml`.
