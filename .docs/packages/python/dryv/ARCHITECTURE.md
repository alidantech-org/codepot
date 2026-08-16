# Dryv final architecture

This document describes the post-migration Dryv architecture implemented by Tasks 00–25. It is the active architecture reference for the Python Runtime and its external clients/backends.

## Three tiers

```text
Authoring
    ↓
Canonical Dryv Runtime IR
    ↓
Templating
    ↓
Usage / generated output
```

The operational boundary is:

```text
Authoring source
    ↓
Author Backend (optional at build time)
    ↓
Canonical Dryv Runtime IR
    ↓
Dryv Runtime validation / indexing / planning / caching
    ↓
Render Sessions
    ↓
Generated artifacts + write instructions
    ↓
Project Client atomic apply
```

## Semantic authority

`dryv.ir` is the only semantic authority.

Authoring implementations may provide expressive language-specific APIs, but they compile into the same versioned Canonical IR. Authoring does not select packs, plan outputs, render templates, or write generated files.

Runtime owns Canonical IR loading, validation, indexing, effective Schema resolution, derived reverse relationships, inspection, and deterministic semantic dependency graphs.

## Dryv Engine Features

The engine is decomposed into explicit Features:

```text
serialization
project
resources
hashing
ir
packs
planning
cache
authoring
templating
scheduling
artifacts
diagnostics
```

Features do not import Runtime or sibling Feature implementations. `dryv.runtime` is the only Dryv owner allowed to coordinate several Features.

### Serialization

Owns deterministic JSON/YAML/JSONL representation mechanics for Canonical IR and canonical representation records.

### Project

Owns `dryv.yaml` meaning. It does not read a project directory; the Project Client supplies the document/resources.

### Resources

Owns logical resource identity/content registry inside a build. A resource is explicit bytes plus media type and content identity, not an arbitrary host path.

### Hashing

Owns versioned canonical hash families for resources, IR records/branches, pack manifests, templates, contexts, renderer fingerprints, artifacts, and build inputs.

### IR Runtime

Owns validation/indexing/resolution over `dryv.ir`, including effective Schema extension, forward/reverse relationships, and semantic dependency graphs.

### Packs

Owns normalized `dryv.pack.yaml` meaning. Packs refer to supplied logical template resources and renderer capabilities. They cannot add Canonical IR semantic concepts or target-language behavior to the Runtime model.

### Planning

Owns deterministic generation intelligence before rendering: selected semantic facts, canonical JSON context, virtual artifacts, dependency order, renderer capability requirements, skipped reasons, and trace/provenance.

The current API accepts explicit normalized `PlanningCandidate` facts because final user-facing selector/grouping vocabulary was intentionally not expanded during Tasks 13–14. This is an explicit contract, not hidden selection magic. Future approved pack-selection vocabulary can move candidate derivation further inside Planning without changing Render Session, Artifact, or Project Client boundaries.

### Cache

Owns versioned Context/Render/Artifact cache records and `use`, `refresh`, `off` policy. Render identity includes context/template/renderer fingerprint/options/protocol facts. Cache mutations are transactional and commit only after a successful Runtime build.

### Authoring

Used only when a project supplies an Author Backend rather than precompiled IR. Runtime receives an established Author Session from the outer host. The Feature validates protocol/source/IR capabilities and passes returned canonical documents/records through Serialization + IR validation.

### Templating

Owns Render Session request/result validation. Runtime supplies an established session. Templating does not execute Jinja/Handlebars or another engine itself.

### Scheduling

Owns bounded queues/channels, dependency readiness, concurrency, session capacity, deterministic eligible-session choice, backpressure, timeout/cancellation, and retry-safe transport retry behavior.

### Artifacts

Owns rendered artifact records, provenance, managed-output comparison, and deterministic write instructions:

```text
CREATE
UPDATE
UNCHANGED
DELETE_MANAGED
```

It never mutates project files.

## Outer host: `dryv-api`

`dryv-api` is the network/process host around Runtime. It owns:

- strict `dryv.api/v1` wire decoding/encoding;
- Render/Author connection registration;
- mapping connection IDs to established sessions;
- build cancellation handles;
- bounded artifact-content transport.

Runtime itself has no HTTP/WebSocket/stdio server dependency.

The repository includes JSONL transports so the architecture can be proven without binding the Engine to one network stack:

```text
python -m dryv_api.stdio
python -m dryv_author.stdio
python -m dryv_template_jinja.stdio
node packages/nodejs/codepotx/render-clients/handlebars/stdio.mjs
```

## Render Clients

A Render Client receives only:

- protocol/context version;
- stable job ID;
- required capability;
- template logical resource/content/hash;
- canonical JSON context/hash;
- planned logical outputs;
- output-affecting render options.

It returns renderer fingerprint, logical output IDs, bytes/hashes, and diagnostics.

It does not receive Canonical IR objects or project filesystem ownership.

The reference proof uses independent Jinja and Handlebars process clients.

## Author Backends

An Author Backend receives logical authored source resources and version/capability requirements. It emits Canonical IR documents/records plus progress/diagnostics.

The Python backend uses `dryv-author` and executes trusted Python author source that exposes `build_author()` or `AUTHOR`. Runtime never imports or executes that author implementation.

Precompiled `dryv.ir.*` bypasses Authoring entirely.

## Project Clients

Project Clients own:

- local source/pack resource acquisition;
- Git/filesystem access and credentials;
- local output-root meaning;
- project file hash observations;
- previous managed-output state;
- staging and atomic apply;
- immediate pre-apply conflict recheck;
- final `apply_complete` acknowledgement.

The Runtime/API response ends at `render_complete`, artifact content, and write instructions.

The Python CLI implements this boundary in `dryv_cli.project_client`. A transport-neutral TypeScript reference exists under `packages/nodejs/dryv-client/src/index.ts` for VS Code/web/desktop/agent hosts.

## Render complete vs apply complete

These states are intentionally different:

```text
render_complete
    Runtime has validated rendering and classified artifacts.

apply_complete
    Project Client has verified the stream, rechecked local hashes,
    atomically applied changes, and persisted managed-output state.
```

A remote Runtime can therefore succeed without claiming that a local project was mutated.

## Incremental cache behavior

Planning records the semantic dependencies used by each context. Hashing composes only reachable semantic branch dependencies. Context/render cache keys use those facts plus relevant pack/template/renderer/protocol identities.

Consequences proven by the Task-23 fixture:

- no change → context/render hits;
- unrelated IR change → unrelated outputs retain hits;
- relevant nested IR change → dependent context/render invalidated;
- template change → only matching render invalidated;
- renderer fingerprint change → only that renderer's render entries invalidated;
- refresh/off explicitly bypass reusable cache reads;
- failed/cancelled builds do not commit pending cache entries.

## Remote project safety

The Task-24 fixture launches `dryv-api` in another process. The temporary project root remains in the parent Project Client process and is not present in the API request.

Only explicit logical resource bytes, project-relative paths, prior managed-output facts, and observed content hashes cross the boundary. The Project Client rechecks the expected hash immediately before applying each update/delete.

## Removed architecture

The active architecture no longer uses:

- `dryv.plugins`;
- `dryv.ports`;
- Runtime plugin discovery;
- embedded `TemplateEngine` ports;
- Source/Target/Writer ports as extension boundaries;
- engine-side `ManagedFilesystemWriter`;
- `generate_to_files`;
- `dryv.template_engines` or `dryv.source_adapters` package entry points.

Permanent architecture tests reject reintroduction of these ownership patterns.

## Executable certification

The repository-editing connector used for Tasks 18–25 has no checkout/test runner, so implementation completion is not represented as executable proof. From a real checkout run:

```bash
uv lock
uv run --all-packages pytest
uv run --all-packages ruff check packages/python/dryv packages/python/dryv-api packages/python/dryv-author packages/python/dryv-cli packages/python/dryv-template-jinja
pnpm install --frozen-lockfile
node packages/nodejs/codepotx/render-clients/handlebars/stdio.mjs </dev/null
git diff --check
```

`uv lock` is specifically required because the migration added the `dryv-api` workspace package and removed old `dryv` dependencies from `dryv-cli` and `dryv-template-jinja`; the connected environment could not regenerate the 267 KB lockfile safely.
