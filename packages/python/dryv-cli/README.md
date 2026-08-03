# dryv-cli

**Status:** Active

`dryv-cli` is the terminal frontend for Dryv. It parses user commands, invokes public runtime operations, presents diagnostics and results, and maps outcomes to stable exit codes.

The CLI does not duplicate Runtime IR, planning, generation, plugin, or ownership logic.

## Local verification

```bash
cd packages/python/dryv-cli
python -m pytest
```

## Canonical documentation

- [CLI documentation](../../../.docs/products/dryv/cli/README.md)
- [Runtime architecture](../../../.docs/products/dryv/runtime/README.md)
- [Dryv task system](../../../.docs/tasks/dryv/README.md)
