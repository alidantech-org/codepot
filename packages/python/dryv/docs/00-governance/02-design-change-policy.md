# Design change policy

Dryv is being implemented across several packages and parallel conversations. Architectural drift is therefore a correctness defect.

## Decision levels

### Locked decisions

Locked decisions are recorded in `00-approved-architecture.md` and `04-closed-semantic-kernel.md`. They require explicit user approval to change.

Examples:

- the closed typed semantic kernel owned only by core;
- growth through deliberate kernel changes rather than plugin-defined facets/objects/selectors;
- outer-to-inner semantic paths and root-first fixed selectors;
- groups, structural schemas, operation inputs/outputs/failures/effects, known facets, views, storage mappings, policies, events, workflows, and compensation;
- no neutral resource/model/entity/frontend/UI roots;
- templates/macros/partials/static files owning every emitted character;
- target adapters limited to detection, validation, and module/path facts;
- the two-file project and pack model;
- no compatibility implementation inside v2;
- `DryvPack.yaml` as the pack contract;
- Python-first application API;
- authored barrel templates and static files copied by default;
- complete planning/validation before rendering;
- command trust, Git lock, ownership-state, and incremental-generation boundaries.

### Package decisions

Package decisions refine locked contracts without changing them. They may be recorded in package design documents and task acceptance criteria.

Examples:

- exact TypeScript filename or module-path validation diagnostics;
- exact Jinja undefined-behavior enum names;
- exact OpenAPI grouping behavior within the approved group contract;
- exact typed `x-codegen` source schema for a known kernel concept;
- exact templates/macros used by one pack product.

A package decision cannot create a new facet, selector, semantic context, syntax renderer, or hidden product/profile mechanism.

### Implementation details

Implementation details may change freely when they preserve public contracts, dependency rules, tests, determinism, and documented behavior.

Examples include private typed graph/index structures, algorithm choices, caching structures, and module organization.

## Required architecture decision record

A change proposal must create:

```text
docs/00-governance/decisions/NNNN-title.md
```

It must contain:

- status: proposed, approved, rejected, or superseded;
- context and real use cases;
- decision and alternatives;
- classification as semantic object, relation, facet, value, selector, context, adapter service, or pack behavior;
- public IR/template-context impact;
- configuration/selector/expression impact;
- plugin/adapter boundary impact;
- generated-syntax ownership impact;
- security/determinism/locking/cache/impact-analysis consequences;
- re-authoring impact;
- task, fixture, conformance, documentation, and behavior-version updates.

No implementation or pack may depend on a proposed decision as though it were approved.

## Kernel growth gate

A new semantic capability is accepted only when the same approved change:

1. defines one framework-neutral meaning;
2. classifies the concept precisely;
3. adds immutable typed models and provenance;
4. defines valid containment/attachment locations;
5. defines source normalization;
6. defines semantic validation and diagnostics;
7. adds root-first fixed selectors where needed;
8. defines immutable template-context exposure;
9. defines deterministic serialization/hashing/ordering;
10. adds realistic source and pack simulations;
11. updates IR/naming/selection/planning behavior versions and compatibility.

Adding an adapter package or arbitrary namespaced key is not a substitute for this process.

## Schema and behavior change rules

- Project, pack, lock, kernel IR, selector, expression, and public adapter contracts are versioned.
- During the initial v2 build, corrections are allowed before stable release, but all active docs/tasks/examples/conformance fixtures must change together.
- After stable release, incompatible document changes require a new `apiVersion`; incompatible kernel/selector behavior requires a new IR or behavior version.
- V2 does not add v1 compatibility decoders.
- Unknown fields/facets/selectors/context properties are errors.
- Bounded documented `extensions`/`raw` values preserve source metadata only; they cannot add semantics or behavior.

## Public Python API change rules

- Supported imports are documented explicitly.
- Internal graph indexes/builders and implementation modules are private.
- Adapters import only their minimum public contracts.
- No public generic semantic node/edge/fact registration API exists.
- A public protocol change updates conformance suites in the same approved change.

## Task synchronization

Every approved decision updates:

1. affected governing and detailed design documents;
2. the master task plan;
3. affected central/package task files;
4. conformance and negative-boundary acceptance criteria;
5. examples and realistic fixtures;
6. package README/design references;
7. progress evidence.
