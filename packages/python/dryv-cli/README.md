# dryv-cli

**Status:** Active

`dryv-cli` is the terminal frontend for Dryv. It parses user commands, invokes public runtime operations, presents diagnostics and results, and maps outcomes to stable exit codes.

The CLI does not duplicate Runtime IR, planning, generation, plugin, or ownership logic.

## Local verification

From the repository root:

```bash
uv run --all-packages pytest packages/python/dryv-cli/tests
uv run --package dryv-cli dryv --help
```

The root workspace supplies the editable `dryv` runtime dependency and exposes the `dryv` console command without manual activation.

## Canonical documentation

- [CLI documentation](../../../.docs/products/dryv/cli/README.md)
- [Runtime architecture](../../../.docs/products/dryv/runtime/README.md)
- [Python workspace](../../../.docs/project/python-workspace.md)
- [Dryv task system](../../../.docs/tasks/dryv/README.md)
