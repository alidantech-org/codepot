# dryv

**Status:** Active

`dryv` is the canonical Python runtime package for Dryv. It owns Runtime IR, canonical validation and transport, plugin contracts, generation planning, inspection, ownership-safe writes, and the public runtime facade.

It does not own authoring syntax, terminal presentation, target-language rendering, or template-engine implementation.

## Local verification

```bash
cd packages/python/dryv
python -m pytest
```

## Canonical documentation

- [Dryv product family](../../../.docs/products/dryv/README.md)
- [Runtime architecture](../../../.docs/products/dryv/runtime/README.md)
- [Approved architecture](../../../.docs/architecture/README.md)
- [Runtime tasks](../../../.docs/tasks/dryv/runtime/README.md)
