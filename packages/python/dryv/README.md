# dryv

`dryv` is the transport-neutral Dryv Engine. It owns Canonical Dryv Runtime IR meaning and the deterministic runtime Features that turn validated IR plus normalized pack declarations into rendered artifacts and Project Client write instructions.

## Architecture

```text
Authoring source / precompiled IR
        |
        v
Canonical Dryv Runtime IR
        |
        v
Dryv Runtime
  Serialization -> IR validation/indexing -> Packs -> Planning
       -> Hashing/Cache -> Scheduling -> Render Sessions -> Artifacts
        |
        v
render_complete + artifact stream + write instructions
        |
        v
Project Client applies locally -> apply_complete
```

The Engine does **not**:

- host HTTP/WebSocket servers;
- discover plugins or template engines;
- execute an author implementation;
- embed Jinja, Handlebars, or another renderer;
- clone pack repositories or resolve Git credentials;
- read or mutate the user's project filesystem;
- report local `apply_complete`.

Those responsibilities live outside `dryv`: `dryv-api` hosts Runtime and established sessions, Author Backends produce Canonical IR, Render Clients render already-planned jobs, and Project Clients own project files.

## Public runtime

```python
from dryv.runtime import DryvRuntime

runtime = DryvRuntime()
print(runtime.snapshot())
```

Cross-Feature composition belongs only to `dryv.runtime`. Individual Feature packages do not import Runtime or sibling Feature implementations.

## Canonical IR

`dryv.ir` is the only semantic authority. Authoring implementations may use Python, TypeScript, Rust, Codepot language, or another implementation, but downstream Runtime and packs consume the same versioned Canonical IR contract.

Runtime owns validation, serialization/loading, indexing, effective Schema resolution, derived reverse relationships, and semantic dependency graphs. Derived indexes are not duplicated into authored state.

## Packs and planning

`dryv.pack.yaml` meaning is owned by `dryv.features.packs`. Packs declare approved generation behavior and logical template resources; all target-language syntax stays in template resources.

Planning produces bounded canonical JSON context, virtual artifacts, dependencies, renderer capability requirements, and provenance **before** rendering begins. Render Clients do not understand Dryv semantics.

## Cache and determinism

Cache identities are versioned and include the relevant semantic dependency hashes, pack/context/template identities, renderer fingerprint, render options, and protocol/context versions. `use`, `refresh`, and `off` are explicit cache modes. Failed or cancelled builds roll back pending cache mutations.

## Artifacts and project ownership

The Engine ends at rendered artifact content plus safe write instructions:

```text
CREATE
UPDATE
UNCHANGED
DELETE_MANAGED
```

The Project Client supplies observed local hashes and the previous managed-output manifest. Dryv refuses unmanaged collisions and modified managed outputs, but it never writes the project itself. The client rechecks hashes immediately before applying changes atomically.

## Protocols

See:

- `.docs/packages/python/dryv/protocols/render-session-v1.md`
- `.docs/packages/python/dryv/protocols/author-session-v1.md`
- `.docs/packages/python/dryv/ARCHITECTURE.md`

## Certification

From a real checkout with Python and Node dependencies installed:

```bash
uv run --all-packages pytest packages/python/dryv/tests
uv run --all-packages pytest packages/python/dryv-api/tests
uv run --all-packages pytest packages/python/dryv-template-jinja/tests
uv run --all-packages ruff check packages/python/dryv packages/python/dryv-api packages/python/dryv-author packages/python/dryv-cli packages/python/dryv-template-jinja
pnpm --filter codepotx exec node render-clients/handlebars/stdio.mjs </dev/null
git diff --check
```

The connected repository-editing environment used for this migration cannot execute those commands; task status distinguishes implementation completion from executable certification.
