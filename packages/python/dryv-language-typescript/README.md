# dryv-language-typescript

**Status:** Active

`dryv-language-typescript` is the TypeScript target adapter for Dryv. It provides target naming, path, module, suffix, keyword, identifier, and validation facts through the public language-adapter contract.

It does not render TypeScript source; templates own emitted syntax.

## Local verification

From the repository root:

```bash
uv run --all-packages pytest packages/python/dryv-language-typescript/tests
```

The root workspace installs this adapter, the Dart adapter, and the local `dryv` runtime together so entry-point integration tests do not require manual environment wiring.

## Canonical documentation

- [TypeScript adapter documentation](../../../.docs/products/dryv/language-typescript/README.md)
- [Language-adapter contract](../../../.docs/architecture/plugins/02-language-adapter-contract.md)
- [Python workspace](../../../.docs/project/python-workspace.md)
- [TypeScript adapter tasks](../../../.docs/tasks/dryv/language-typescript/README.md)
