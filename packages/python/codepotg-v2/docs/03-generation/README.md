# 03 — Generation, selection folders, and output safety

Generation is planned from the pack filesystem, fixed selectors, registered selection folders, explicit imports/exports/symbols, bindings, and adapter rules. No renderer or writer is called until the complete plan is valid.

## Mandatory documents

1. [`00-path-expressions-and-name-tokens.md`](00-path-expressions-and-name-tokens.md) — `{selectionKey}`, `{root}`, `(expression)`, `((literal))`, naming, and source-path compilation.
2. [`01-template-file-model.md`](01-template-file-model.md) — filesystem discovery, templates, static/binary files, partials, barrels, symbols, and engine/target inference.
3. [`02-selection-folder-patterns-and-static-files.md`](02-selection-folder-patterns-and-static-files.md) — fixed selectors, nested selection folders, explicit imports, exports, barrels, aggregates, and static fan-out.
4. [`03-planning-execution-and-transaction.md`](03-planning-execution-and-transaction.md) — invocation graphs, validation, rendering, transactions, and cache.

## Locked generation rules

- `templates/` is the default discovered content root.
- Literal files preserve their pack-relative paths.
- Only `{selectionKey}` folders require manifest registration; `{root}` emits at the pack output root.
- Dynamic path/name values use `(expression)` and literal parentheses use `((value))`.
- Square brackets remain literal for framework routes.
- Semantic IR records do not expose invented `fileName`, `filePath`, or `directory` values.
- Fixed `.each`/`.all` selectors replace arbitrary pack-authored `from`/`as` declarations.
- Static and binary files are copied automatically; `_partials` is not emitted.
- Generated dependencies are explicit through `imports`, `exports`, and `symbols` selection keys.
- Barrels are authored templates and may export other barrels.
- The engine suffix is stripped; target suffixes remain.
- Every destination, import, export, dependency, command, approval, and collision is planned before rendering.
