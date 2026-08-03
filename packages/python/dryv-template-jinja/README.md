# dryv-template-jinja

**Status:** Active

`dryv-template-jinja` is the Jinja template-engine adapter for Dryv. It provides bounded rendering, helper registration, dependency analysis, caching, diagnostics, and sandbox enforcement through the runtime's public template-engine contract.

It does not define canonical software meaning or target-language semantics.

## Local verification

```bash
cd packages/python/dryv-template-jinja
python -m pytest
```

## Canonical documentation

- [Jinja adapter documentation](../../../.docs/products/dryv/template-jinja/README.md)
- [Template-engine adapter contract](../../../.docs/architecture/plugins/03-template-engine-adapter-contract.md)
- [Template tasks](../../../.docs/tasks/dryv/template-jinja/README.md)
