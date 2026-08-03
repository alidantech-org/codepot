# dryv-author

**Status:** Active

`dryv-author` is the Python authoring frontend for Dryv. It lets users express software meaning through typed Python helpers and compiles that meaning into the canonical Dryv Runtime IR.

Authoring does not generate application files, select packs, define output paths, write output, or own Runtime IR serialization.

## Local verification

From the repository root:

```bash
uv run --all-packages pytest packages/python/dryv-author/tests
uv run --all-packages mypy packages/python/dryv-author/src
uv run --all-packages pyright packages/python/dryv-author
```

The root workspace supplies the local `dryv` dependency. Do not connect packages through `PYTHONPATH`, editable `pip` installs, or a package-local virtual environment.

## Canonical documentation

- [Authoring documentation](../../../.docs/products/dryv/authoring/README.md)
- [Architecture rules](../../../.docs/architecture/README.md)
- [Python workspace](../../../.docs/project/python-workspace.md)
- [Authoring tasks](../../../.docs/tasks/dryv/authoring/README.md)
