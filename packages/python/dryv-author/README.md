# dryv-author

**Status:** Active

`dryv-author` is the Python authoring frontend for Dryv. It lets users express software meaning through typed Python helpers and compiles that meaning into the canonical Dryv Runtime IR.

Authoring does not generate application files, select packs, define output paths, write output, or own Runtime IR serialization.

## Local verification

```bash
cd packages/python/dryv-author
python -m pytest
```

## Canonical documentation

- [Authoring documentation](../../../.docs/products/dryv/authoring/README.md)
- [Architecture rules](../../../.docs/architecture/README.md)
- [Authoring tasks](../../../.docs/tasks/dryv/authoring/README.md)
