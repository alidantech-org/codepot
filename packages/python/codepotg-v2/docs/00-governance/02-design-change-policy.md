# Design change policy

CodepotG v2 is being implemented across several packages and parallel conversations. Architectural drift is therefore treated as a correctness defect.

## Decision levels

### Locked decisions

Locked decisions are recorded in `00-approved-architecture.md`. They require explicit user approval to change.

Examples:

- the two-file project and pack model;
- no compatibility implementation inside v2;
- template-owned target language;
- `CodepotgPack.yaml` as the pack contract;
- Python-first application API;
- typed adapter rules and overrides;
- authored barrel templates;
- static files copied by default;
- command trust boundaries.

### Package decisions

Package decisions refine a locked decision without changing it. They may be recorded in package design documents and task acceptance criteria.

Examples:

- exact TypeScript reserved-word escape format;
- exact Jinja undefined behavior enum names;
- OpenAPI diagnostic codes.

### Implementation details

Implementation details may change freely when they preserve public contracts, dependency rules, tests, and documented behavior.

## Required architecture decision record

A change proposal must create a document under:

```text
docs/00-governance/decisions/NNNN-title.md
```

It must contain:

- status: proposed, approved, rejected, or superseded;
- context;
- decision;
- alternatives considered;
- public API impact;
- configuration impact;
- plugin impact;
- security impact;
- migration or re-authoring impact;
- task and test updates.

No implementation may depend on a proposed decision as though it were approved.

## Schema change rules

- Core project and pack schemas are versioned public contracts.
- During the initial v2 build, schema corrections are allowed before the first stable release, but all fixtures and examples must be updated together.
- After the first stable release, incompatible changes require a new `apiVersion`.
- V2 does not add v1 compatibility decoders. A new v2 schema version may provide a v2-to-v2 migration only when approved.
- Unknown fields are errors unless they are under a registered namespaced extension point.

## Public Python API change rules

- Supported imports are documented explicitly.
- Internal modules use private naming and are not extension points.
- Adapters import only public plugin, IR, configuration, diagnostic, and testing contracts.
- A change to a public protocol requires conformance-suite updates in the same commit.

## Task synchronization

Every approved decision must update:

1. the affected design document;
2. the master task plan;
3. affected package task files;
4. conformance acceptance criteria;
5. examples and fixtures;
6. the progress ledger.
