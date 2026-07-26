# TypeScript SDK pack task tracking

Read:

1. `../design/README.md`;
2. the v2 pack manifest specification;
3. `codepotg-v2/docs/03-generation/00-path-expressions-and-name-tokens.md`;
4. central agent rules and `PARALLEL_WORK.md`.

- Claim PACK-TS task IDs before implementation.
- Ordinary files must derive destinations from tokenized source paths, not `model.fileName`, `operation.fileName`, or manifest output strings.
- Mark `[x]` only after manifest, templates, path recipes, static files, bindings, setup/actions, focused tests, realistic fixtures, docs, and progress evidence pass.
- Record exact test/tool commands in `PROGRESS.md`.
- Author only the new v2 pack; do not implement old `paths.yaml` behavior.

Task files:

- [`00-package-plan.md`](00-package-plan.md)
- [`01-path-authoring.md`](01-path-authoring.md)
