# Codepot evidence and validation program

## Purpose

Codepot should be developed as an engineering hypothesis that earns stronger claims through evidence. This document defines the experiments, metrics, and claim gates required to establish effectiveness.

## Claim maturity

### Demonstrated

A claim may be labeled demonstrated only when:

- the exact behavior is implemented on the named commit;
- reproducible tests or project evidence exist;
- the packaged artifacts, not only source checkouts, have been validated where relevant;
- limitations and environment are recorded;
- evidence can be independently repeated.

### Architecturally supported

Use this label when:

- the approved design provides a coherent mechanism;
- some implementation evidence exists;
- full package-family or end-to-end verification is incomplete.

### Unproven

Use this label for expected productivity, adoption, safety, migration, marketplace, or AI-agent outcomes until measured.

## Current claim matrix

| Claim | Current grade from reviewed repository | Evidence needed to advance |
|---|---|---|
| Typed OpenAPI authoring can emit deterministic portable contracts | Demonstrated historically | maintain regression fixtures |
| OpenAPI-driven Jinja packs can generate real project artifacts | Demonstrated historically | preserve representative archive fixtures |
| Managed/immutable output and guarded cleanup are practical | Demonstrated historically in CodepotG, current-line revalidation needed | failure-injection and packaged Dryv tests |
| The Dryv package split and closed-kernel architecture are coherent | Architecturally supported | exact-head full package-family verification |
| Multiple authoring frontends can produce equivalent IR | Unproven as a product guarantee | cross-language conformance corpus |
| Cross-pack planning can coordinate complete projects | Architecturally supported | multi-pack real-project evolution |
| Codepot reduces engineering time and defects | Unproven | controlled baseline studies |
| Codepot makes AI agents safer and more effective | Unproven | agent comparison trials |
| Framework migration becomes materially cheaper | Unproven | migration case study |
| A pack marketplace can be sustainable | Unproven | long-lived pack ecosystem evidence |

## Validation layers

## 1. Semantic kernel validation

Required evidence:

- valid and invalid fixtures for every object and relation;
- stable diagnostic codes and source paths;
- canonical ordering and digests;
- JSON/YAML round trips;
- stable identity across rename and movement;
- compatibility classification tests;
- version migration fixtures;
- bounded extension/raw preservation;
- no plugin or pack can add a semantic kind.

Exit condition:

> Two independent implementations can read the canonical contract and agree on identities, ordering, validation results, and digest.

## 2. Authoring conformance

Create a shared language-neutral corpus containing:

- declaration scenarios;
- expected canonical contracts;
- expected diagnostics;
- expected stable identities and provenance;
- invalid reference and duplicate cases;
- derivation and mapping cases;
- operation, event, policy, storage, view, and workflow cases.

Every authoring frontend must compile the corpus to semantically equivalent Runtime IR. Byte-identical transport is preferred after canonical serialization, but semantic equivalence is the governing requirement.

Exit condition:

> Authoring language choice does not alter runtime planning or generated output for equivalent declarations.

## 3. Pack conformance

Each pack is tested for:

- manifest validity;
- selector compatibility;
- context access boundaries;
- deterministic discovery;
- path portability;
- declared symbols and dependencies;
- missing/ambiguous provider diagnostics;
- template sandbox behavior;
- static and binary file handling;
- option and binding coverage;
- deterministic rendered output;
- managed ownership declarations;
- compatibility range behavior.

Exit condition:

> A pack can be validated and simulated independently from an application project.

## 4. Planner validation

Test complete graphs containing:

- several groups and nested groups;
- schemas reused in several operation directions;
- several pack instances;
- cross-pack generated dependencies;
- barrels and aggregate artifacts;
- duplicate destinations and symbols;
- cycles;
- bindings and overrides;
- commands and approvals;
- additions, updates, removals, and unchanged artifacts;
- compatibility warnings and blocks;
- impact from semantic and template changes.

Property tests should verify that planning order does not depend on map iteration, filesystem enumeration, plugin discovery order, or parallel scheduling.

Exit condition:

> Every renderer input and writer action is already registered and validated in the plan.

## 5. Writer and transaction validation

Use failure injection at every stage:

- staging file creation;
- content rendering completion;
- permission checks;
- replacement of existing files;
- stale deletion;
- state write;
- command execution boundaries;
- cancellation;
- process interruption;
- concurrent invocation.

Test:

- unmanaged collisions;
- edited managed files;
- unchanged stale files;
- changed stale files;
- symlinks and path escape;
- case-insensitive collisions;
- Windows reserved names and separators;
- rollback after partial failure;
- lock recovery.

Exit condition:

> A failed or cancelled generation leaves the project and ownership state at the last valid committed state.

## 6. Pack distribution and trust validation

Test local and Git sources with:

- branches, tags, and commits;
- subdirectories;
- private repositories through normal credentials;
- immutable lock resolution;
- moved branches after lock;
- content digest mismatch;
- missing credentials;
- command approval changes;
- cached pack corruption;
- offline locked resolution where supported.

Exit condition:

> The exact source and behavior used for generation are reproducible without recording credentials.

## 7. Generated-project validation

A runtime test is incomplete until generated targets are verified with their own toolchains.

For every reference pack family:

- compile or type-check generated code;
- run generated tests;
- apply and reverse test migrations where relevant;
- run format/lint checks;
- install generated package dependencies from a controlled lock;
- exercise a minimal runtime flow;
- verify API/SDK interoperability;
- inspect documentation links;
- rerun generation and confirm no diff.

Exit condition:

> Generated artifacts are accepted by the target ecosystem and deterministic reruns are clean.

## 8. Cross-machine reproducibility

Run the same locked project on:

- Linux;
- Windows;
- macOS when supported;
- at least two filesystem case-sensitivity profiles;
- clean isolated environments.

Compare:

- canonical contract digest;
- dependency lock;
- plan digest;
- artifact paths and digests;
- diagnostics;
- ownership state excluding explicitly host-local facts.

Exit condition:

> Behaviorally relevant outputs match across supported platforms.

## 9. Real-project evolution study

Select at least two independent projects using the same pack family. Perform a sequence over several weeks:

1. initial contract and generation;
2. add a field;
3. add an operation;
4. add a relation and storage index;
5. rename a schema while preserving identity;
6. make a deliberate breaking change;
7. add an event consumer;
8. change pack version;
9. customize handwritten behavior;
10. remove a semantic concept and clean stale output;
11. migrate one target pack or framework version;
12. reproduce from a clean checkout.

Record defects, time, review effort, and manual intervention.

Exit condition:

> The projects remain comfortable to evolve; regeneration is routine rather than feared.

## 10. Baseline productivity experiment

Compare three workflows on equivalent tasks:

### Baseline A — conventional tools

OpenAPI or schema tool, ORM, framework conventions, scripts, and manual edits.

### Baseline B — AI direct editing

An agent receives repository instructions and edits all required files directly.

### Treatment — AI or human through Codepot

The semantic change is made through authoring/IR, planned, generated, and verified.

Measure:

- elapsed and active engineering time;
- files inspected and modified;
- missing artifacts;
- inconsistencies;
- test failures;
- review time;
- corrective iterations;
- token/tool usage for agents;
- confidence before and after verification;
- maintenance cost of supporting tools.

Tasks must include both favorable and unfavorable Codepot cases to avoid designing a benchmark that only rewards generation.

Exit condition:

> Codepot provides statistically and practically meaningful lifecycle improvement for the target use case.

## 11. Agent safety and effectiveness experiment

Agents receive the same requirement and repository state. Compare:

- direct filesystem/repository editing;
- Codepot public runtime operations only;
- hybrid workflow where custom logic is edited directly and repeated structure goes through Codepot.

Evaluate:

- semantic correctness;
- architecture compliance;
- unintended changes;
- successful verification;
- retries;
- clarity of final explanation;
- provenance completeness;
- recovery from invalid requests;
- resistance to editing generated files directly;
- ability to identify requirements outside the kernel.

The hybrid workflow is likely the realistic target.

Exit condition:

> Codepot reduces inconsistent or unintended agent changes without increasing total task cost beyond an acceptable threshold.

## 12. Usability study

Recruit participants who did not implement the runtime:

- application developers;
- platform engineers;
- pack authors;
- one authoring-frontend implementer.

Observe tasks from [`usability-and-adoption.md`](usability-and-adoption.md). Record time, errors, questions, confidence, and source-code lookups.

Exit condition:

> Users complete core workflows from public documentation and diagnostics without maintainer intervention.

## 13. Migration experiment

Use one real contract and generate two different target stacks or two major versions of a stack.

Classify work as:

- automatically derived;
- pack/binding changes;
- handwritten adapter changes;
- custom algorithm rewrites;
- data migration;
- operational migration;
- unresolved semantic mismatch.

Compare with a conventional rewrite estimate and actual baseline where possible.

Exit condition:

> Codepot measurably reduces rediscovery and repetitive migration work while making residual custom work explicit.

## Metrics dashboard

Track at least:

### Correctness

- semantic validation failures by code;
- compatibility issues caught before generation;
- generated-target failure rate;
- nondeterministic reruns;
- manual-edit conflicts;
- rollback failures;
- stale artifact errors.

### Productivity

- median time for reference changes;
- plan-to-generation time;
- review time;
- corrective iterations;
- pack reuse count;
- percentage of repeated artifacts derived.

### Usability

- time to first generation;
- diagnostic resolution rate;
- pack-author completion rate;
- documentation search paths;
- user prediction accuracy;
- abandonment rate.

### Ecosystem health

- supported pack versions;
- pack conformance status;
- time to framework-version support;
- security incidents;
- deprecated-pack migration completion;
- runtime/plugin compatibility failures.

### Agent behavior

- task success;
- unintended file changes;
- direct generated-file edits attempted;
- diagnostics consumed correctly;
- token/tool-call cost;
- final explanation completeness.

## Kill and narrow criteria

Narrow or stop a product direction when repeated evidence shows:

- most generated files require manual edits;
- one pack is the only consumer of most kernel concepts;
- project configuration costs more than repeated implementation;
- developers avoid regeneration;
- pack upgrades repeatedly break handwritten extensions;
- cross-frontend equivalence cannot be maintained;
- runtime and pack maintenance exceed saved project cost;
- agent workflows are slower and no safer than direct editing;
- users cannot understand plans or ownership;
- compatibility warnings are routinely bypassed because they lack value.

These are not failures of ambition. They are signals to reduce scope and preserve the valuable core.

## Evidence publication rule

Every major claim in public documentation should link to:

- a dated experiment or verification report;
- the exact commit and package versions;
- the project/fixture used;
- commands and environment;
- raw results or artifacts;
- limitations and known failures.

Codepot should be unusually honest about what is designed, implemented, verified, and observed in production. That honesty will strengthen trust more than broad unsupported claims.
