# dryv

**Status:** Active

`dryv` is the canonical Python runtime package for Dryv. It owns Runtime IR, canonical validation and transport, plugin contracts, generation planning, inspection, ownership-safe writes, and the public runtime facade.

It does not own authoring syntax, terminal presentation, target-language rendering, or template-engine implementation.

## Local verification

From the repository root:

```bash
uv run --all-packages pytest packages/python/dryv/tests
```

Do not create or activate a package-local virtual environment. The root `uv` workspace installs this package and all connected members in editable mode.

## Canonical documentation

- [Dryv product family](../../../.docs/products/dryv/README.md)
- [Runtime architecture](../../../.docs/products/dryv/runtime/README.md)
- [Approved architecture](../../../.docs/architecture/README.md)
- [Python workspace](../../../.docs/project/python-workspace.md)
- [Runtime tasks](../../../.docs/tasks/dryv/runtime/README.md)
