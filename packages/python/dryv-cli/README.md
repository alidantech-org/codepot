# dryv-cli

`dryv-cli` is a Dryv **Project Client**. It talks to the versioned Dryv API and owns local project resource collection, file observation, managed-output state, conflict checks, atomic apply, and the final `apply_complete` acknowledgement.

It does not import or orchestrate `dryv.runtime`.

## Build flow

```text
local project
   |
   | collect explicit logical resources + local hash observations
   v
dryv.api/v1 request
   |
   v
dryv-api / remote Dryv Runtime
   |
   | render_complete + artifact stream + write instructions
   v
dryv-cli
   |
   | recheck hashes, stage, atomically apply, persist managed-output state
   v
apply_complete
```

The local project root is never sent to Runtime. Only explicit logical resources and project-relative observations cross the API boundary.

## Command

```bash
dryv build request.json --root .
```

By default the CLI starts/connects to:

```bash
python -m dryv_api.stdio
```

A different API command can be supplied with `--api-command` or `DRYV_API_COMMAND`.

The request file uses the strict `dryv.api/v1` wire contract. It contains logical resource IDs/bytes, normalized pack/template inventory, planning facts, an IR source, renderer connection IDs, previous managed-output facts, and project-relative observed hashes. The CLI never adds its local root path to the request.

## Local apply safety

`dryv_cli.project_client`:

- streams artifact bytes into staging storage;
- verifies artifact size and SHA-256 content identity;
- refuses unsafe or traversing paths;
- rechecks `expectedPreviousHash` immediately before mutation;
- refuses unmanaged CREATE collisions;
- rolls back partial writes on failure;
- writes `.dryv/managed-outputs.json` only after generated file changes succeed.

`render_complete` is a Runtime/API fact. `apply_complete` exists only after the Project Client has committed the local changes.

## Validation

```bash
uv run --all-packages pytest packages/python/dryv-api/tests/integration/test_remote_runtime_local_project.py
uv run --all-packages ruff check packages/python/dryv-cli
```
