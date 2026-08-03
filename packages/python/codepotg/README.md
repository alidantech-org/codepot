# CodepotG

> **Status: Frozen**
>
> CodepotG is retained for existing users and historical comparison. It is not an active development target. Do not add features, redesign it, or modernize it unless a ready task explicitly authorizes narrow maintenance.

CodepotG is the earlier Python OpenAPI-oriented generator and Jinja pack system that informed the active Dryv architecture.

Active development happens in the [`dryv` package family](../dryv/README.md).

## Frozen maintenance verification

CodepotG participates in the root `uv` workspace so an explicitly approved maintenance task can reproduce its environment without a package-local virtual environment:

```bash
uv run --all-packages pytest packages/python/codepotg/tests
```

Workspace membership does not change CodepotG's frozen status and does not make it a dependency of Dryv.

## Canonical documentation

- [Frozen CodepotG record](../../../.docs/products/frozen/codepotg/README.md)
- [Component status](../../../.docs/project/component-status.md)
- [Python workspace](../../../.docs/project/python-workspace.md)
- [Dryv product family](../../../.docs/products/dryv/README.md)
