# dryv-language-dart

**Status:** Active

`dryv-language-dart` is the Dart target adapter for Dryv. It provides target naming, path, module, package, keyword, identifier, and validation facts through the public language-adapter contract.

It does not render Dart source; templates own emitted syntax.

## Local verification

From the repository root:

```bash
uv run --all-packages pytest packages/python/dryv-language-dart/tests
```

The root workspace installs this adapter, the TypeScript adapter, and the local `dryv` runtime together so entry-point integration tests do not require manual environment wiring.

## Canonical documentation

- [Dart adapter documentation](../../../.docs/products/dryv/language-dart/README.md)
- [Language-adapter contract](../../../.docs/architecture/plugins/02-language-adapter-contract.md)
- [Python workspace](../../../.docs/project/python-workspace.md)
- [Dart adapter tasks](../../../.docs/tasks/dryv/language-dart/README.md)
