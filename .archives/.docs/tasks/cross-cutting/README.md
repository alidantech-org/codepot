# Cross-cutting tasks

Use this area only when a change genuinely spans several active components or repository-wide policy.

A cross-cutting task must name one coordinating owner, list every affected component, define file ownership boundaries, and split implementation into non-overlapping child tasks when concurrent work is expected.

Do not use this area to avoid choosing the real owning component.

## Current tasks

- [`python-uv-workspace.md`](python-uv-workspace.md) — one `uv` workspace, environment, lock, and connected development workflow for every package under `packages/python/`.
