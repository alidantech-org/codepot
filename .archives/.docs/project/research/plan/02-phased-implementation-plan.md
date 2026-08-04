# Phased implementation plan

## Planning principle

Implement Codepot from semantic authority outward. Do not begin with a marketplace, many target packs, a visual editor, or agent automation. Each phase must produce a stable contract and evidence that the next layer can depend on.

The phases describe architecture outcomes, not programming-language tasks.

## Phase 0 — charter, baseline, and evidence design

### Objective

Establish exactly what problem the first release will solve and how success will be measured.

### Deliverables

- product definition and anti-goals;
- current architecture map;
- authoritative document order;
- historical package/support matrix;
- two real reference projects;
- one initial multi-output pack family;
- conventional and AI-direct-editing baselines;
- claim maturity register;
- initial security and trust model;
- decision and change-governance process.

### Rules

- The first release is not universal.
- Select a domain with repeated schemas, operations, storage, SDK, and documentation work.
- Record existing task time and failure patterns before introducing Codepot.
- Freeze terminology for the first implementation cycle.

### Exit criteria

The team can state which workflows Codepot intends to improve, which it does not, and which evidence will decide continuation.

## Phase 1 — canonical semantic contract

### Objective

Define the smallest complete Runtime IR required by the reference slice.

### Deliverables

- typed immutable contract model;
- stable identity rules;
- groups and structural schemas;
- operations with inputs, outputs, failures, and selected approved facets;
- events and storage mappings required by the reference projects;
- naming, documentation, provenance, tags, and bounded extensions;
- canonical ordering and digest rules;
- validation and diagnostic catalog;
- canonical JSON/YAML transport;
- compatibility model and version policy;
- contract conformance corpus.

### Rules

- Include only concepts required by at least two realistic outputs.
- No framework classes or folder structures enter the kernel.
- Every reference has a known kind and resolution rule.
- Every collection has deterministic ordering.
- Every field and relation has compatibility behavior.

### Exit criteria

Independent readers can validate, serialize, compare, and digest the same contract identically.

## Phase 2 — authoring compiler contract

### Objective

Prove that expressive authoring can compile into the canonical contract without becoming a second semantic system.

### Deliverables

- one reference authoring frontend;
- declaration models and typed references;
- deterministic author session and linking;
- stable ID assignment or explicit identity support;
- source spans and provenance;
- reusable properties and explicit schema derivation;
- authoring diagnostics mapped to canonical diagnostics;
- canonical conformance fixtures;
- host-supplied in-memory contract provider;
- canonical transport loader as an equal input route.

### Rules

- Authoring builders never enter template contexts.
- Invalid authoring returns diagnostics rather than partial hidden state.
- Compilation is deterministic and side-effect free.
- Authoring does not serialize, select packs, or write output.

### Exit criteria

The same reference contract can be loaded from canonical transport or produced by authoring with equivalent runtime behavior.

## Phase 3 — pack contract and discovery

### Objective

Define a portable pack that can be inspected and validated independently.

### Deliverables

- pack identity and compatibility model;
- filesystem discovery rules;
- manifest for non-inferable behavior;
- template, partial, static, and binary classification;
- fixed selector registry;
- path-expression and naming contract;
- options and public bindings;
- declared selections, symbols, imports, exports, and commands;
- pack diagnostics and conformance fixtures;
- pack documentation schema.

### Rules

- Literal filesystem behavior is inferred safely.
- Only dynamic selection folders require registration.
- Packs cannot add selectors or semantics.
- Templates cannot access unbounded runtime or source objects.
- Manifest order and filesystem enumeration do not affect results.

### Exit criteria

A pack can be validated, documented, and simulated before being connected to a project.

## Phase 4 — immutable planning engine

### Objective

Calculate the complete generation graph before rendering.

### Deliverables

- project/usage configuration model;
- direct local and Git source references;
- pack instance resolution;
- selector evaluation;
- invocation and artifact identity model;
- destination normalization;
- symbol/provider/dependency graph;
- binding and option resolution;
- collision, ambiguity, cycle, and capability checks;
- command and approval plan;
- compatibility and impact report;
- explanation graph;
- stable plan digest and serialization.

### Rules

- Planning is pure relative to render/write side effects.
- Every artifact destination is known before rendering.
- Every generated dependency has one declared provider.
- Invalid plans cannot be rendered.
- Plan output is the same for interactive and non-interactive clients.

### Exit criteria

The reference projects produce complete, stable plans that explain every artifact and fail deterministically for every invalid fixture.

## Phase 5 — rendering boundary

### Objective

Render planned immutable contexts without granting renderers semantic or filesystem authority.

### Deliverables

- template-engine adapter contract;
- immutable prepared context schemas;
- sandbox and resource limits;
- partial/include dependency tracking;
- target adapter contract for validation and module/path facts;
- deterministic text and binary output model;
- structured render diagnostics;
- in-memory generation result;
- render reproducibility tests.

### Rules

- Renderers cannot select semantics or destinations.
- Target adapters cannot emit syntax.
- Templates own every emitted character.
- Context values are documented, typed, bounded, and immutable.
- Rendering to memory is fully supported before filesystem writing.

### Exit criteria

The same valid plan always produces identical in-memory artifacts under the same locked behavior inputs.

## Phase 6 — managed transactional output

### Objective

Apply generated artifacts safely to real projects.

### Deliverables

- ownership/generation-state model;
- staged write set;
- unmanaged and modified-managed conflict handling;
- unchanged stale cleanup;
- transactional commit and rollback;
- project/output locking;
- path and symlink safety;
- cancellation and recovery;
- dry-run parity;
- state and artifact trace persistence;
- failure-injection suite.

### Rules

- The writer consumes a valid plan and rendered artifacts; it does not invent behavior.
- State changes only after artifact commit.
- Visible partial output is not an acceptable failure mode.
- Destructive actions are explicit in the plan.

### Exit criteria

Injected failures and cancellation leave both reference projects at their previous valid state.

## Phase 7 — lock, trust, and distribution

### Objective

Make project and pack behavior reproducible and safe across machines.

### Deliverables

- dependency lock format;
- mutable-ref to immutable-commit resolution;
- pack content digests;
- plugin and behavior identities;
- cache integrity checks;
- credential redaction and normal Git authentication;
- trust and command-approval records;
- offline/frozen behavior policy;
- package installation and discovery conformance;
- source provenance in plans and traces.

### Rules

- Locks record behavior inputs, not credentials.
- Marketplace aliases never replace complete source identity.
- Remote commands are untrusted by default.
- Runtime, frontend, and plugins use public package contracts only.

### Exit criteria

A clean environment can reproduce the same plan and artifacts from the locked project using authorized credentials only for source retrieval.

## Phase 8 — explanation, compatibility, and inspection product

### Objective

Make the runtime understandable without internal debugging.

### Deliverables

- inspect contract/project/pack/plugin/lock/state operations;
- semantic diff and compatibility report;
- artifact plan and blast-radius views;
- bidirectional trace queries;
- explanation of selection, skip, path, binding, and dependency decisions;
- stable machine schemas;
- concise human presentation model;
- IDE and agent-friendly pagination/filtering.

### Rules

- Explanations are derived from structured plan/trace artifacts, not log parsing.
- Every frontend receives the same underlying facts.
- Compatibility detection and policy decisions are visibly separate.

### Exit criteria

An unfamiliar developer can diagnose the reference failure scenarios from public diagnostics and explanation operations.

## Phase 9 — reference pack family

### Objective

Prove coordinated multi-artifact derivation on real software.

### Deliverables

At minimum, connected packs for:

- service/API boundaries;
- storage/migration representation;
- one client SDK;
- documentation or contract inspection.

The pack family includes:

- realistic fixtures;
- target-project verification;
- extension guidance;
- compatibility declarations;
- upgrade and removal procedure;
- cross-pack dependency examples.

### Rules

- Prefer depth and repeated evolution over many frameworks.
- Generated output must be idiomatic enough for target developers to maintain and debug.
- Custom business logic remains handwritten through documented boundaries.

### Exit criteria

The pack family survives the complete reference evolution sequence in two projects.

## Phase 10 — frontend and agent integration

### Objective

Expose the stable runtime through several interfaces without duplicating behavior.

### Deliverables

- thin CLI;
- machine-readable non-interactive interface;
- optional IDE or server integration;
- agent/MCP operations for inspect, validate, compare, plan, explain, generate, and verify;
- authorization and side-effect metadata;
- cancellation and idempotency semantics;
- agent evaluation harness.

### Rules

- Frontends do not import private runtime implementation.
- Agents do not receive hidden write capabilities.
- Human confirmation affects authorization only, never planning.
- Machine output remains stable and presentation-free.

### Exit criteria

A human and an agent can complete the same reference change through the same public runtime lifecycle and produce equivalent results.

## Phase 11 — effectiveness evaluation

### Objective

Decide whether the product delivers net value.

### Deliverables

- conventional baseline comparison;
- AI-direct-editing comparison;
- human and agent Codepot workflows;
- usability study;
- migration case study;
- maintenance-cost accounting;
- reliability and rollback evidence;
- published limitations and kill/narrow decisions.

### Rules

- Include tasks that do not favor Codepot.
- Measure correction and review time, not only initial completion.
- Record runtime and pack maintenance cost.
- Do not generalize beyond the tested domain.

### Exit criteria

The team can identify the use cases where Codepot wins, loses, and should not be used.

## Phase 12 — controlled expansion

### Objective

Expand only from proven contracts.

Possible expansions:

- second authoring language;
- additional target adapters and template engines;
- views, presentations, advanced workflows, or policies;
- richer compatibility policies;
- conservative incremental generation;
- pack certification and discovery service;
- organizational governance services;
- native Codepot language.

### Entry requirement

Each expansion has real demand, a compatibility plan, conformance fixtures, and no need to weaken existing boundaries.

## Prohibited sequencing

Do not:

- build a marketplace before trust, locks, and pack conformance;
- build a native language before the canonical IR and authoring conformance corpus stabilize;
- implement incremental generation before correct full generation;
- support many targets before one pack family survives evolution;
- expose arbitrary plugin semantics to accelerate ecosystem growth;
- make the CLI the only complete interface;
- label the system production-ready before packaged end-to-end verification;
- promise full-project generation before generated/handwritten ownership is comfortable.

## Program checkpoints

At the end of every phase, publish:

- exact commit and package versions;
- completed and deferred contracts;
- reproducible verification commands;
- failing or skipped evidence;
- compatibility impact;
- architecture decisions;
- updated claim maturity;
- whether scope should continue, narrow, or stop.
