# 03 — Generation, path composition, and output safety

Generation is planned from pack source files, typed selections, named path recipes, bindings, dependencies, and adapter rules. No renderer or writer is called until the complete plan is valid.

## Mandatory documents

1. [`00-path-expressions-and-name-tokens.md`](00-path-expressions-and-name-tokens.md) — source paths as output programs, `{recipe}` expansion, `[expression]` tokens, casing, and original/singular/plural naming.
2. [`01-template-file-model.md`](01-template-file-model.md) — unified template, barrel, static, binary, partial, and documentation descriptors.
3. [`02-selection-folder-patterns-and-static-files.md`](02-selection-folder-patterns-and-static-files.md) — selections, path-recipe fan-out, descriptor patterns, static content, and profiles.
4. [`03-planning-execution-and-transaction.md`](03-planning-execution-and-transaction.md) — invocation graphs, validation, rendering, transactions, and cache.

## Locked generation rules

- The content-root-relative source path is the default output-path expression.
- Semantic IR records do not expose invented `fileName` or `directory` values.
- Named path recipes live under `CodepotgPack.yaml` `paths` and are referenced with `{recipe}`.
- Typed dynamic values use `[expression]` and support stable casing plus original/singular/plural projections.
- The recognized template-engine suffix is stripped; the target suffix remains.
- Static and binary files are emitted by default after the same path-token expansion.
- Barrels are authored template files, not system-generated files.
- Explicit output overrides use the same bounded path grammar and are exceptional.
- Every output, import, dependency, and command is planned before rendering.
