# Governance and contribution guide

## Purpose

Codepot’s architecture depends on maintaining boundaries over time. This guide defines how a team should organize ownership, approve semantic growth, review packs and plugins, preserve historical evidence, and prevent convenience changes from weakening determinism.

## Governance principles

1. Public contracts are products, not implementation details.
2. Semantic growth is slower and more rigorous than pack growth.
3. Evidence outranks architectural confidence.
4. Compatibility changes are explicit and reviewable.
5. Historical implementations remain evidence, not hidden obligations.
6. Every exception has an owner, scope, expiry, and migration path.
7. Humans and AI agents follow the same contribution and runtime boundaries.

## Ownership groups

A small team may combine roles, but responsibilities remain distinct.

### Semantic kernel owners

Own:

- Runtime IR objects, relations, facets, and values;
- identity, ordering, canonical transport, and compatibility;
- selector and context contracts;
- kernel conformance corpus;
- semantic version and migration policy.

Must not own target-specific templates as part of kernel decisions.

### Authoring owners

Own:

- language-native declarations and references;
- compiler passes and source diagnostics;
- source provenance;
- authoring conformance to canonical IR.

Must not add frontend-specific semantics or generation behavior.

### Planning and generation owners

Own:

- project and pack loading;
- selection and invocation planning;
- dependency/symbol resolution;
- path planning;
- impact and explanations;
- rendering coordination;
- managed output and state.

Must not redefine meaning or emit target syntax in core.

### Plugin and distribution owners

Own:

- capability descriptors and discovery;
- target and engine adapter conformance;
- source and pack providers;
- locks, caches, trust, and package integration.

Must not grant plugins semantic extension authority.

### CLI and client owners

Own:

- human presentation;
- interaction and confirmation;
- machine protocol adapters;
- IDE, web, notebook, and agent integrations.

Must consume public runtime operations only.

### Pack maintainers

Own:

- target implementation architecture;
- templates and static content;
- options, bindings, symbols, and dependencies;
- generated project verification;
- extension points, upgrades, and migration guidance.

Must not require private runtime access or hidden semantic conventions.

## Normative document hierarchy

The repository should publish a clear order similar to:

1. approved architecture and non-negotiable principles;
2. closed semantic kernel contract;
3. public runtime and plugin contracts;
4. generation, ownership, lock, and trust contracts;
5. authoring frontend contracts;
6. pack authoring contracts;
7. implementation plans and tasks;
8. examples and tutorials;
9. historical and archived documentation.

Lower documents cannot override higher ones. A contradiction is a release blocker until resolved.

## Architecture decision records

Create an architecture decision record for changes involving:

- semantic object, relation, facet, or value;
- public selector or context property;
- identity, ordering, serialization, or digest behavior;
- compatibility rules;
- plugin capability or trust boundary;
- pack manifest behavior;
- output ownership or transaction policy;
- public runtime operations;
- supported product/package topology.

An ADR contains:

- problem and evidence;
- decision;
- alternatives;
- effects on every tier;
- compatibility and migration;
- security and determinism impact;
- conformance fixtures;
- rollout and rollback;
- explicit non-goals.

## Kernel change procedure

A kernel proposal proceeds through these gates:

### 1. Evidence gate

Provide at least two real use cases and show why existing concepts, relationships, tags, guidance, bindings, or pack logic are insufficient.

### 2. Neutrality gate

Define the concept without target framework, language, database, or folder vocabulary.

### 3. Topology gate

Specify identity, owner, attachment, references, ordering, and whether it is an object, relation, facet, or value.

### 4. Runtime reasoning gate

Explain why validation, compatibility, selection, impact, or trace needs the concept.

### 5. Cross-target simulation

Show different packs using the same semantic fact differently.

### 6. Cross-authoring simulation

Show how at least two authoring styles can produce the same IR.

### 7. Compatibility gate

Define additions, removals, modifications, defaults, and migration behavior.

### 8. Contract gate

Add schemas, diagnostics, selectors, contexts, transport, digests, and conformance fixtures.

### 9. Adoption gate

Document author and pack usability. Reject proposals that make common workflows disproportionately complex.

### 10. Version gate

Select the required behavior/schema version and support window.

A proposal is not approved merely because it can be typed.

## Pack contribution procedure

A new or changed pack provides:

- product use case and target compatibility;
- source and maintenance owner;
- manifest and filesystem conformance;
- documented selectors, contexts, options, and bindings;
- explicit symbols and dependencies;
- realistic fixtures;
- generated-target verification;
- deterministic snapshots;
- ownership and handwritten extension guidance;
- security and command review;
- upgrade, deprecation, and exit plan.

Pack changes should usually not require kernel changes. When they do, evaluate the kernel proposal independently.

## Plugin contribution procedure

A plugin proposal identifies one bounded capability. It provides:

- stable ID and version;
- public capability contract;
- lifecycle and factory behavior;
- least-authority requirements;
- deterministic discovery and conflict behavior;
- conformance tests;
- failure and diagnostic mapping;
- security review;
- proof that it does not add semantics or target emission outside its boundary.

Import-time global registration is prohibited.

## Compatibility governance

### Detection and policy

Runtime compatibility detection is objective according to a published behavior version. Project or organizational policy decides whether to block, warn, or allow.

### Waivers

A waiver records:

- exact diagnostic/rule;
- affected identity and baseline;
- rationale;
- approver;
- scope;
- expiry or review point;
- downstream migration plan.

Waivers do not erase the compatibility result.

### Deprecation

Public contracts receive:

- announcement;
- replacement guidance;
- support window;
- diagnostics where feasible;
- migration fixtures;
- final removal version.

Indefinite compatibility shims are avoided.

## Documentation governance

### Active truth

Root documentation identifies:

- current architecture;
- package names and roles;
- stable, preview, experimental, and archived status;
- normative documents;
- exact verification status;
- latest migration path.

### Archives

Archived documents remain available for research. Each archive header states:

- why it is archived;
- active replacement;
- concepts still valid;
- concepts explicitly superseded;
- whether compatibility is supported.

### Examples

Examples are executable release artifacts. They are versioned with the contracts they demonstrate and verified during release.

## Task and pull-request discipline

Every implementation task states:

- governing contract;
- owned subsystem;
- explicit non-goals;
- public artifacts affected;
- compatibility impact;
- tests and evidence;
- generated-project verification when relevant;
- documentation updates;
- cleanup of superseded behavior.

Reviews reject changes that:

- bypass a layer for convenience;
- create hidden semantics;
- add a second behavior source;
- weaken planning or output safety;
- introduce target syntax into core;
- depend on private modules across packages;
- change machine contracts without versions;
- claim more maturity than evidence supports.

## AI-agent contribution rules

Agents may implement, test, and document changes, but they must:

- read normative architecture first;
- identify the owned tier;
- use public contracts;
- preserve exact branch and repository policies;
- report assumptions and unresolved contradictions;
- run required evidence gates;
- avoid creating new semantic concepts as incidental fixes;
- distinguish authored changes from generated output;
- provide traceable commits and summaries.

Agent-produced architecture changes receive the same human review as any other change.

## Release governance

A release owner collects evidence from all relevant subsystem owners. Release status is based on the weakest required connected gate, not the strongest individual package.

The release report records:

- exact commit;
- package and behavior versions;
- normative contract versions;
- supported platforms;
- conformance and integration results;
- generated-target results;
- unresolved failures/skips;
- compatibility and migration notes;
- security/trust changes;
- claim maturity.

## Ecosystem governance

### Pack discovery

A future catalog or marketplace helps users find packs. It does not:

- replace full source identity;
- hold required private credentials;
- grant automatic trust;
- bypass lock or content digest;
- imply quality solely from listing.

### Quality signals

Publish:

- conformance version and result;
- supported runtime/IR/target ranges;
- fixture and generated-project coverage;
- last verified date;
- maintainer identity;
- security and command capabilities;
- deprecation status.

### Naming

Reserve official naming only for packs maintained under documented service and compatibility expectations. Third-party packs use the same technical contracts without receiving hidden privileges.

## Conflict-resolution principle

When priorities conflict, use this order:

1. protect user files and security;
2. preserve semantic authority and compatibility truth;
3. preserve deterministic behavior and reproducibility;
4. preserve public contract stability;
5. preserve explainability;
6. improve usability;
7. improve performance;
8. add breadth and convenience.

Performance and convenience never justify silent semantic or destructive behavior.

## Governance health metrics

Track:

- kernel proposals accepted/rejected and rationale;
- time to resolve architecture contradictions;
- compatibility waivers and expiry;
- deprecated behavior remaining;
- packs using raw/extensions for normal behavior;
- private-contract violations;
- release evidence gaps;
- framework update latency for official packs;
- contributor onboarding time;
- user-reported explanation gaps;
- percentage of public claims linked to evidence.

## Final governance rule

Codepot remains strong only when architecture boundaries survive success. More users, packs, plugins, and agent integrations increase pressure for shortcuts. Governance must make extension possible without making meaning ambiguous.
