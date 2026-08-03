# dryv-template-jinja

**Status:** Active

`dryv-template-jinja` is the Jinja template-engine adapter for Dryv. It provides bounded rendering, helper registration, dependency analysis, caching, diagnostics, and sandbox enforcement through the runtime's public template-engine contract.

It does not define canonical software meaning or target-language semantics.

## Local verification

From the repository root:

```bash
uv run --all-packages pytest packages/python/dryv-template-jinja/tests
```

The root workspace installs both this adapter and the local `dryv` runtime in editable mode. Distribution tests use `uv` for builds and isolated environments.

## Canonical documentation

- [Jinja adapter documentation](../../../.docs/products/dryv/template-jinja/README.md)
- [Template-engine adapter contract](../../../.docs/architecture/plugins/03-template-engine-adapter-contract.md)
- [Python workspace](../../../.docs/project/python-workspace.md)
- [Template tasks](../../../.docs/tasks/dryv/template-jinja/README.md)
