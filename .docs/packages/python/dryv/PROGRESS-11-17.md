# Dryv Tasks 11–17 implementation checkpoint

## Scope

This checkpoint covers implementation work for Tasks 11 through 17 only:

- Task 11 — Hashing Feature
- Task 12 — IR Runtime Feature
- Task 13 — Packs Feature
- Task 14 — Planning and Template Context Feature
- Task 15 — Cache Feature
- Task 16 — Templating Feature
- Task 17 — Authoring Feature

Task 18 is not started by this checkpoint.

The implementation began from the Task-10 checkpoint at commit `90ccb90e4dbb1d52c58a998c618f77c091add029` and remained on `develop`; no branch was created.

## Task 11 — Hashing

Implemented under `dryv.features.hashing`:

- one explicit SHA-256/version-1 canonical hash contract;
- typed hash purposes for resource content, canonical documents, IR records, IR branches, pack manifests, template content, context, renderer fingerprints, artifact content and build inputs;
- stable canonical JSON-compatible bytes;
- deterministic branch hashing over reachable semantic dependencies only;
- structured missing-record and dependency-cycle errors;
- stable build-input composition;
- a literal golden canonical-document hash vector;
- legacy generated-artifact ownership hashing routed through `HashPurpose.ARTIFACT_CONTENT`.

A legacy exception remains in `dryv.infrastructure.ir_source`: its existing source-adapter `digest` still uses a local SHA-256 checksum. That adapter already consumes the Serialization Feature; making it also coordinate Hashing would violate the new Feature boundary. It is therefore explicitly bounded to the Task-21 legacy infrastructure migration rather than treated as a second canonical/build hashing authority.

## Task 12 — IR Runtime

Implemented under `dryv.features.ir`:

- canonical Contract validation and deterministic `SemanticIndex` construction;
- one immutable runtime snapshot containing semantic objects, direct dependencies, reverse dependents and derived relationship indexes;
- effective Schema resolution through the canonical Schema extension rules;
- derived Event emitter/listener, Schema→Operation, Schema→StorageMapping and View→Presentation relationships;
- Event-trigger Operations included in derived listener relationships;
- bounded deterministic external-record indexing with duplicate and size-limit errors;
- injected record decoder support so Runtime can compose Serialization without an IR→Serialization Feature dependency;
- duplicate validation diagnostics removed from the load path.

## Task 13 — Packs

Implemented under `dryv.features.packs` as the current owner of normalized `DryvPack.yaml` meaning:

- approved manifest vocabulary only: identity/version/description, requirements, include/exclude, options, bindings, selections, executables and commands;
- strict unknown-field rejection and deterministic normalization;
- option/default/choice and binding validation;
- selection import/export/binding reference validation;
- safe relative selection paths;
- explicit supplied template-resource records with logical resource id, media type, selection relationship and required renderer capability;
- renderer capability is an inventory/resource fact, not a newly invented `DryvPack.yaml` field;
- manifest logical-resource provenance and stable selection pointers;
- legacy `dryv.config` Pack model/decoder ownership reduced to Task-21 compatibility adapters that delegate to the Packs Feature.

The old `dryv.generation` implementation remains a Task-21 migration surface and is not the new Packs authority.

## Task 14 — Planning and template context

Implemented under `dryv.features.planning`:

- deterministic planning candidates, invocations and virtual artifacts;
- explicit planned/skipped state with required skip reasons;
- stable selection/template/renderer/semantic dependency facts;
- explicit used option and binding names;
- stable trace facts for explainability;
- bounded canonical JSON-compatible template context with context versioning;
- structured rejection of non-finite numbers and unsupported context values;
- safe project-relative output paths;
- required artifact dependency validation;
- artifact dependency cycle diagnostics;
- deterministic topological artifact ordering before rendering;
- stable canonical plan document/bytes.

Planning consumes normalized candidate facts supplied by Runtime composition rather than importing IR or Packs sibling Feature internals.

## Task 15 — Cache

Implemented under `dryv.features.cache`:

- separate versioned Context, Render and Artifact cache-key families;
- `use`, `refresh` and `off` modes;
- Context keys include semantic dependency hashes, projection version, pack hash and input hash;
- Render keys include context/template/renderer fingerprint/render options/protocol/context-version facts;
- Artifact keys include artifact identity and build-input hash;
- replaceable `CacheStore` protocol plus in-memory implementation;
- transaction-scoped pending writes with commit/rollback;
- refresh ignores stale reads while allowing replacement;
- disabled and non-committing plan/dry-run transactions do not mutate storage;
- failed work can roll back without poisoning prior valid entries;
- deterministic cache-entry serialization for replaceable persistence.

Cache accepts hash identities; it does not implement a competing hash algorithm.

## Task 16 — Templating

Implemented under `dryv.features.templating`:

- renderer hello/capability contract;
- protocol/context/media-type negotiation;
- stable renderer fingerprint/capacity/determinism facts;
- render requests carrying job id, logical template resource, template hash/content, canonical context/hash, planned outputs and render options;
- structured renderer diagnostics;
- cancellation propagation;
- validation of canonical JSON-compatible context/options;
- result job/fingerprint validation;
- duplicate, unknown and missing output rejection;
- output content-hash validation through an injected Hashing-owned callback;
- no template-engine import or server transport inside Dryv.

The language-neutral wire authority is documented in `protocols/render-session-v1.md`.

The legacy `dryv.ports.templates.TemplateEngine` contract remains a Task-21 compatibility surface; it is not the new Render Session authority.

## Task 17 — Authoring

Implemented under `dryv.features.authoring`:

- Author Backend hello/capability contract;
- protocol/source-kind/IR-version negotiation;
- logical resource based source requests;
- progress, diagnostics, streamed IR record, complete-document and completion message contracts;
- streamed canonical records passed directly to an injected Serialization decoder;
- document outputs passed to an injected media-type decoder;
- exactly one canonical representation mode per job;
- streaming records require advertised backend streaming support;
- stable job/fingerprint checks;
- cancellation propagation while consuming author messages;
- produced Contract validation through an injected IR validator before downstream use;
- precompiled Canonical IR bypasses Authoring entirely.

The language-neutral wire authority is documented in `protocols/author-session-v1.md`.

No author language implementation is imported into Dryv.

## Architecture decisions preserved

- `dryv.ir` remains the only semantic authority.
- Features do not import Runtime.
- New Tasks 11–17 Features do not import sibling Feature implementations.
- Cross-Feature composition is expressed through injected callbacks/plain normalized facts and remains Runtime work for Task 20.
- Packs do not add semantic meaning or target-language vocabulary.
- Planning does not render or write files.
- Cache does not define hashing.
- Templating does not execute an embedded template engine.
- Authoring does not execute/import an author implementation.
- No HTTP/WebSocket server behavior was added.
- No Task-18 Scheduling implementation is included.

## Executable certification status

The connected GitHub environment does not expose a repository checkout, CI/status runner, or remote shell. The execution container cannot resolve external network hosts, so the package test and Ruff commands have not been falsely recorded as passing.

Run these commands from a real checkout of the repository:

```bash
uv run --all-packages pytest packages/python/dryv/tests/architecture
uv run --all-packages pytest packages/python/dryv/tests/unit/features/hashing
uv run --all-packages pytest packages/python/dryv/tests/unit/features/ir
uv run --all-packages pytest packages/python/dryv/tests/unit/features/packs
uv run --all-packages pytest packages/python/dryv/tests/unit/features/planning
uv run --all-packages pytest packages/python/dryv/tests/unit/features/cache
uv run --all-packages pytest packages/python/dryv/tests/unit/features/templating
uv run --all-packages pytest packages/python/dryv/tests/unit/features/authoring
uv run --all-packages pytest packages/python/dryv/tests/unit/config/test_loader.py
uv run --all-packages pytest packages/python/dryv/tests
uv run --all-packages ruff check packages/python/dryv
git diff --check 90ccb90e4dbb1d52c58a998c618f77c091add029 HEAD
```

Do not advance Task 18 on the basis of this document alone if those executable checks reveal a Tasks 11–17 regression. Fix the regression within its owning Feature first.
