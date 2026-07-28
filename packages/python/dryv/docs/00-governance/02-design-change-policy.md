# Design change policy

Dryv spans several packages and workflows. Architectural drift is therefore a correctness defect.

## Decision levels

### Locked decisions

Locked decisions are recorded in the approved architecture and closed-kernel documents. They require explicit user approval to change.

Examples:

- one closed typed semantic kernel owned by Dryv core;
- growth through deliberate kernel changes rather than plugin-defined objects, facets, selectors, or context roots;
- root-first fixed selectors and public naming projections;
- groups, structural schemas, operations, known facets, views, storage mappings, policies, events, value sources, workflows, presentations, and typed relationships;
- no neutral resource/model/entity/frontend/UI framework roots;
- templates, macros, partials, and static files own every emitted character;
- target plugins are limited to detection, validation, and module/path facts;
- `dryv.yaml` and `DryvPack.yaml` own project and pack configuration;
- no archived compatibility implementation;
- Python-first reusable runtime API;
- standalone CLI interface;
- complete planning and validation before rendering;
- explicit command trust, Git lock, ownership state, and incremental-generation boundaries.

### Package decisions

Package decisions refine locked contracts without changing them. They may define:

- exact language filename, identifier, or module-path diagnostics;
- exact template-engine limits or undefined behavior;
- exact contract-provider loading diagnostics;
- target capability descriptors;
- templates, macros, and static files for one pack product.

A package decision cannot create a new semantic object, facet, selector, context root, syntax renderer, hidden product profile, or runtime bypass.

### Implementation details

Private data structures, algorithms, cache strategies, and module organization may change when they preserve public contracts, dependency direction, tests, determinism, security, and documented behavior.

## Architecture decision records

A change proposal creates:

```text
docs/00-governance/decisions/NNNN-title.md
```

It records:

- status;
- context and real use cases;
- decision and alternatives;
- precise concept classification;
- public IR and context impact;
- configuration, selector, and expression impact;
- plugin and package-boundary impact;
- generated-text ownership impact;
- security, determinism, locking, caching, and impact-analysis consequences;
- migration/re-authoring impact;
- tasks, fixtures, tests, docs, and behavior-version changes.

No implementation or pack may depend on a proposed decision as though it were approved.

## Kernel growth gate

A new semantic capability is accepted only when the same approved change:

1. defines one framework-neutral meaning;
2. classifies the concept precisely;
3. adds immutable typed models and provenance;
4. defines valid ownership and relationships;
5. defines authoring/provider mapping where needed;
6. defines validation and diagnostics;
7. adds fixed selectors only when justified;
8. defines immutable prepared-context exposure;
9. defines deterministic transport, hashing, and ordering;
10. adds realistic contract and pack fixtures;
11. updates relevant API and behavior versions.

Installing a plugin or adding an arbitrary namespaced value is not a substitute for this process.

## Schema and behavior changes

- Project, pack, lock, IR, selector, expression, runtime, and plugin contracts are versioned.
- Before stable release, corrections may be made, but code, tests, docs, examples, fixtures, and task plans change together.
- After stable release, incompatible document changes require a new `apiVersion`; incompatible semantic/planning behavior requires a new behavior version.
- Dryv does not add archived compatibility decoders.
- Unknown fields, facets, selectors, and context properties are errors.
- Bounded documented extension/raw values preserve provenance only; they cannot add behavior.

## Public Python API changes

- Supported imports are documented explicitly.
- Private indexes, builders, and implementation modules remain private.
- Plugins import only their minimum public contracts.
- No public generic semantic-node/edge/fact registration API exists.
- Protocol changes update conformance suites in the same approved change.
- Runtime and CLI interfaces remain separate packages.

## Synchronization

Every approved decision updates:

1. governing and detailed design documents;
2. the master plan;
3. affected package task files;
4. conformance and negative-boundary tests;
5. examples and realistic fixtures;
6. package READMEs and cookbook recipes;
7. progress and release evidence.
