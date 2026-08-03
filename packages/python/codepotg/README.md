# CodepotG

> **Status: Frozen**
>
> CodepotG is retained for existing users and historical comparison. It is not an active development target. Do not add features, redesign it, or modernize it unless a ready task explicitly authorizes narrow maintenance.

CodepotG is the earlier Python OpenAPI-oriented generator and Jinja pack system that informed the active Dryv architecture.

Active development happens in the [`dryv` package family](../dryv/README.md).

## Workspace participation

CodepotG participates in the root `uv` workspace so dependency resolution remains reproducible for an explicitly approved maintenance task. It is intentionally excluded from the root active-package pytest collection.

The restored CodepotG implementation still contains legacy archive-qualified imports. Do not repair, test, or modernize that frozen implementation as part of ordinary Dryv work; create a ready frozen-maintenance task that defines the exact compatibility scope first.

Workspace membership does not change CodepotG's frozen status and does not make it a dependency of Dryv.

## Canonical documentation

- [Frozen CodepotG record](../../../.docs/products/frozen/codepotg/README.md)
- [Component status](../../../.docs/project/component-status.md)
- [Python workspace](../../../.docs/project/python-workspace.md)
- [Dryv product family](../../../.docs/products/dryv/README.md)
