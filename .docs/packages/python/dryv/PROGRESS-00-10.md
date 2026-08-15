# Dryv Tasks 00–10 implementation checkpoint

Date: 2026-08-16
Branch: `develop`

## State

Implementation for Dryv Tasks 00 through 10 is present on `develop`.

This checkpoint distinguishes **implementation completion** from **external executable certification**. The connected GitHub environment used for this work exposes no repository checkout, no Codespace/remote shell, and no CI/status checks for these commits. The full pytest/Ruff/git-diff commands therefore have not been falsely recorded as passing.

Do not begin Task 11 until the certification commands at the end of this document pass or any failures they expose are fixed.

## Task 00 — Runtime/Feature boundaries

Implemented:

- the approved 13-Feature catalog under `dryv.features`;
- Runtime/Feature/IR dependency-direction architecture tests;
- public-Feature-root consumption rules;
- Runtime-only multi-Feature coordination policy;
- server-hosting dependency/import rejection;
- narrow Task 21 legacy exceptions.

Primary implementation checkpoint: `142ec213719ed19525e0f1c02dbaec0db2c023e5`.

## Task 01 — Canonical IR ownership

Implemented:

- `dryv.ir` is the canonical public semantic authority;
- semantic definitions moved under `dryv.ir` with compatibility-only `dryv.domain.ir` shims;
- production imports converge on `dryv.ir`;
- transport ownership removed from canonical IR and moved to Serialization;
- architecture tests enforce canonical ownership and IR independence from Features.

Key checkpoints include `cd6ab9e`, `0d37480`, and later ownership hardening through the current tree.

## Task 02 — Contract, Group, Property

Implemented:

- canonical Contract/Group/Property semantics;
- reusable typed Property references;
- global semantic-ID duplicate detection and deterministic indexing;
- Group-owned semantic roots stop at Properties/Schemas/Policies/Failures/Events/Operations/StorageMappings/ValueSources/Views;
- Workflow ownership corrected to the Contract root as required by the task model;
- architecture test now enforces that `Contract` has a `workflows` dataclass field and `Group` does not.

Workflow ownership correction checkpoints: `f8b0545`, `c3d330d`, `c6bbaf8`, `e4c72f6`, `69af74a`, plus fixture/test migrations.

`Group.workflows` remains a read-only empty compatibility property only so bounded legacy code does not crash before later Planning/Packs cleanup. It is not authorable semantic ownership.

## Task 03 — Schema and single-base extension

Implemented:

- zero/one direct `Schema.extends` base;
- transitive deterministic effective-schema resolution;
- missing-base and cycle diagnostics;
- kind compatibility;
- explicit field override references;
- implicit same-name override rejection;
- incompatible override rejection;
- stable inherited-field ordering;
- inspectable effective field origins;
- inherited fields respected by StorageMapping, ValueSource and field-reference validation.

## Task 04 — Policy, Failure, Event

Implemented:

- reusable canonical Failure identities and typed Schema payload references;
- Policy context/composition references with cycle validation;
- Event payload/context/policy references;
- forward relationship ownership without Event reverse-authorship lists;
- deterministic uniqueness checks.

Key hardening checkpoint: `0529b98`.

## Task 05 — Operation

Implemented:

- semantic absence and one/many named inputs/outputs;
- canonical Failure and Policy references;
- subject Schema references;
- typed Operation relationships (`invokes`, `requires`, `delegates_to`, `before`, `after`, `triggers_workflows`);
- Event emission/consumption through typed effects/facets;
- missing-reference and invalid order/requirement/delegation cycle diagnostics;
- no generated Controller/Service/Command/Query roots introduced.

Key hardening checkpoint: `a47ee54`.

## Task 06 — StorageMapping, ValueSource, View

Implemented:

- explicit Schema-to-storage mapping without modifying Schema meaning;
- mapped, storage-only, generated and computed storage fields;
- omitted fields, primary keys, unique constraints, indexes, checks, storage references, version fields and serialization facts;
- effective inherited Schema fields used for storage validation;
- ValueSource named outputs/value/label/search/dependent-input references;
- ValueSource dependency cycle validation;
- View Schema/field/ValueSource/Operation/Workflow/Event/View relationships;
- reference validation without authored reverse lists.

Key hardening checkpoints: `08e6b25`, `6f80184`, `6e16b46`.

## Task 07 — Workflow, Presentation, cross-cutting semantics

Implemented:

- Contract-owned Workflow roots;
- operation steps, child-workflow steps, decisions, parallel branches, waits, transitions and compensation;
- Failure/Event/Policy/Operation relationships and child-workflow cycle diagnostics;
- Presentation entries referencing Views plus Policies/Operations/Events/Workflows;
- presentation navigation-cycle diagnostics;
- shared tags, documentation, guidance and provenance;
- guidance categories include `explain`, `implement`, `warn`, `security`, persistence/caching/testing/observability/UX/accessibility and existing neutral categories;
- transport round-trip coverage now includes Contract-owned Workflows.

Important correction: earlier incremental code inherited Group-owned Workflow placement from the legacy model. The Task 02/07 contract was re-read and the model was corrected to Contract ownership before this checkpoint.

## Task 08 — Serialization Feature

Implemented under `dryv.features.serialization`:

- deterministic Contract JSON/YAML codec ownership;
- canonical portable record representation;
- JSON/YAML record encoding/decoding;
- bounded chunked JSONL iteration;
- byte offset/length indexing;
- strict representation/version/key checks;
- canonical semantic Contract → record splitting → Contract reconstruction;
- Contract JSONL streaming using stable semantic record IDs;
- canonical per-record bytes and SHA-256 record hashes;
- missing/duplicate/cyclic record detection;
- public IR boundary use only (`dryv.ir`, not `dryv.ir.model` from Serialization);
- legacy IR source adapter routes JSON, YAML and `.jsonl` through Serialization.

Key later checkpoints: `af04a36`, `3afaf7b`, `5c56a37`, `01754a9`, `ae33d16`, `70dd54b`, `b680cbb`.

## Task 09 — Project Feature

Implemented under `dryv.features.project`:

- canonical meaning/validation for `dryv.yaml` usage configuration;
- IR-resource, Author-Backend and bounded legacy-source forms with source-mode exclusivity;
- pack instances, options, bindings and safe logical output roots;
- logical resources;
- cache modes `use`, `refresh`, `off`;
- build modes `render`, `plan`, `stream`;
- renderer capability/session preferences;
- deterministic source/pack/resource normalization;
- project Feature contains no filesystem or Git acquisition behavior.

`dryv.config.models` is compatibility-only for Project semantics: its Project/Source/PackInstance/PackSource types are imported from the Project Feature. Pack-manifest semantics intentionally remain there until the dedicated Packs Feature task.

Primary Project checkpoint: `317ad35`, with renderer-preference hardening in the follow-up commits.

## Task 10 — Resources Feature

Implemented under `dryv.features.resources`:

- portable `resource://` logical identities;
- safe path-like normalization and traversal/host-path rejection;
- media type, size, SHA-256 content hash and bounded origin metadata;
- in-memory byte and stream registration with configured size limits;
- content-hash verification and immutable reuse;
- lookup by logical ID and content hash;
- bounded full/chunked reads;
- deterministic resource manifests;
- logical-ID/content conflict detection;
- missing-resource and missing-blob/hash negotiation for remote-build reuse;
- no Git, credential, arbitrary project-path acquisition or artifact writes inside the Feature.

Primary Resources checkpoint: `323a460`.

## Known intentionally deferred compatibility

These are not unfinished Tasks 00–10 semantics:

- `dryv.domain.ir` compatibility shims remain bounded by Task 21;
- legacy generation/selection vocabulary is not finalized here; Tasks 02/07 explicitly defer selection syntax and later Packs/Planning tasks own that migration;
- the legacy selector name `groups.workflows.each` may remain until that migration, while canonical authored Workflow ownership is Contract-level;
- `OperationFailure` remains an explicit compatibility value until the separate `dryv-author` migration; canonical `Operation.failures` and `Workflow.failures` contain Failure IDs;
- `dryv-author` still requires its own planned tasks to become an independent Canonical IR producer and is intentionally not silently refactored as part of Dryv Tasks 00–10.

## Source-level audit performed

The implementation was re-read against the actual Task 01–10 documents after the first incremental pass. That audit found and corrected, among other issues:

- explicit Schema overrides rather than implicit same-name replacement;
- inherited effective-field use in storage/value-source/reference validation;
- missing Policy composition/Event policy semantics;
- missing Operation relationship families;
- missing richer Storage/ValueSource/View relationships;
- child Workflow composition;
- Contract-level Workflow ownership;
- stale duplicate ValueSource validation that ignored inherited fields;
- generic JSONL that was not yet a real Contract semantic-record round trip;
- Serialization importing `dryv.ir.model` instead of the public `dryv.ir` boundary;
- the legacy IR source adapter lacking JSONL routing;
- a stale test importing transport from `dryv.ir`;
- missing `warn` guidance category.

## External certification gate

Run from the repository root on the current `develop` branch:

```bash
uv run --all-packages pytest packages/python/dryv/tests/architecture
uv run --all-packages pytest packages/python/dryv/tests
uv run --all-packages ruff check packages/python/dryv
uv run --all-packages pyright packages/python/dryv || true

git diff --check 98ae0ce5ba8ec98aa013bcda9a4ecbec5005bab2 HEAD
```

If the repository does not use `pyright` as an installed package check, use the static typing command currently configured by the workspace instead; do not add a new type checker merely for this gate.

At this checkpoint GitHub exposes no status checks for the branch commits, and the connected execution container cannot resolve/download the repository. Therefore this document records implementation evidence but deliberately does **not** claim the commands above passed.

## Next task

After the certification gate is green, continue with:

`Task 11 — Build the Hashing Feature`
