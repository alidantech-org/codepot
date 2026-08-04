# Validation and release gates

## Principle

No Codepot component is release-ready merely because its unit tests pass. The release unit is the connected behavior consumed by a user: authoring or loading a contract, resolving packs and plugins, planning, rendering, writing safely, and validating generated targets.

## Gate 1 — normative contracts

Required:

- architecture and responsibility boundaries approved;
- current package/product names documented;
- public schemas and operation versions fixed for the release;
- compatibility policy recorded;
- historical and experimental behavior labeled;
- no unresolved contradiction among normative documents.

Failure condition:

Two active documents assign the same responsibility to different tiers.

## Gate 2 — canonical IR

Required:

- all objects and relationships immutable;
- stable IDs, ordering, serialization, and digests;
- valid/invalid conformance corpus;
- round trips for supported transports;
- semantic comparison and compatibility fixtures;
- source provenance retained without frontend objects;
- extension/raw boundaries tested;
- migration behavior for supported prior versions.

Failure condition:

Equivalent contracts can produce different canonical digests.

## Gate 3 — authoring/source conformance

Required for each source frontend:

- shared canonical fixture suite passes;
- diagnostics match expected codes and semantic locations;
- wrong-kind, duplicate, missing, forward, and foreign reference cases pass;
- no process-global state affects compilation;
- no source-specific object reaches Runtime IR;
- compilation remains free of generation side effects.

Failure condition:

Equivalent declarations change plan or output based on authoring language.

## Gate 4 — pack and plugin conformance

Required:

- public descriptors and capability versions validated;
- discovery is deterministic and instance-owned;
- missing, duplicate, conflicting, and unsupported capabilities produce structured diagnostics;
- pack filesystem and manifest validation passes;
- selectors and context schemas match runtime versions;
- engine sandbox and target boundaries are verified;
- no plugin extends the semantic kernel;
- pack fixtures produce deterministic expected plans and artifacts.

Failure condition:

Import order or filesystem enumeration changes behavior.

## Gate 5 — planner correctness

Required:

- every artifact, destination, symbol, dependency, option, binding, command, approval, and ownership action is present before rendering;
- collision, ambiguity, path, cycle, and capability fixtures pass;
- plan ordering and digest are stable;
- dry run uses the executable plan;
- compatibility and impact appear in the plan;
- explanation edges exist for selected and skipped behavior;
- invalid plans cannot reach rendering.

Failure condition:

A renderer or writer discovers a new behavior-affecting fact.

## Gate 6 — rendering determinism

Required:

- same plan and locked inputs produce identical bytes;
- static and binary files preserve intended content;
- template dependencies are tracked;
- sandbox/resource violations produce structured errors;
- renderer has no destination or filesystem authority;
- target adapter emits no syntax;
- output content digest is stable.

Failure condition:

Rerendering without changed inputs changes an artifact.

## Gate 7 — managed output safety

Required:

- unmanaged collision protection;
- modified managed-file protection;
- conservative stale cleanup;
- path traversal, symlink, case, Unicode, and reserved-name tests;
- staging, atomic replacement where supported, and rollback;
- state commit ordering;
- cancellation and concurrent-run safety;
- failure injection at every commit step;
- exact dry-run/execution action parity.

Failure condition:

A failed, cancelled, or conflicting generation loses user work or leaves invalid state.

## Gate 8 — source lock and trust

Required:

- local and Git sources resolve predictably;
- mutable refs lock to immutable commits;
- pack content and manifest digests verify;
- credentials are absent from configuration, locks, state, and diagnostics;
- remote commands are visible and approved according to policy;
- cache corruption is detected;
- frozen mode rejects unrecorded behavior changes;
- clean-environment reproduction succeeds.

Failure condition:

The same lock can resolve to different pack content.

## Gate 9 — package/distribution integrity

Required for every distributed component:

- package builds successfully;
- artifact contents match declared public modules and assets;
- clean isolated installation succeeds;
- entry-point/plugin discovery succeeds using installed packages;
- runtime has no accidental dependency on CLI/presentation packages;
- frontend packages use public runtime contracts only;
- package versions and compatibility ranges align;
- license, metadata, documentation, and source links are correct.

Failure condition:

Tests pass from a source checkout but the installed package family cannot perform the reference workflow.

## Gate 10 — generated target verification

Required for each reference pack:

- generated projects compile or type-check;
- format/lint validation passes;
- generated tests pass;
- storage migrations are validated where relevant;
- service and SDK communicate in a minimal flow;
- generated docs resolve links and references;
- repeated generation creates no diff;
- custom handwritten extension points remain intact.

Failure condition:

Runtime tests pass while generated targets fail their own ecosystem tools.

## Gate 11 — cross-platform reproducibility

Required:

- supported operating systems run the same locked reference project;
- canonical, plan, and artifact digests match where expected;
- internal path representations are portable;
- line-ending and executable-bit policy is explicit;
- case-sensitive and case-insensitive collisions are handled;
- diagnostics and actions remain behaviorally equivalent.

Failure condition:

A supported host silently generates a different project structure.

## Gate 12 — evolution and compatibility

Required:

The reference project completes at least:

- field addition;
- stable-identity rename;
- operation addition;
- deliberate breaking change;
- event or policy change;
- storage relation/index change;
- semantic removal and stale cleanup;
- pack upgrade;
- handwritten extension preservation;
- clean checkout reproduction.

Failure condition:

The system works only for initial generation.

## Gate 13 — usability

Required:

An unfamiliar developer completes the reference lifecycle from public documentation and diagnostics. A pack author creates or modifies a bounded pack without inspecting runtime internals.

Measure:

- completion rate;
- active time;
- diagnostic resolution;
- prediction accuracy before generation;
- source-code lookups;
- manual generated-file edits;
- confidence and recovery.

Failure condition:

Maintainer guidance is routinely required for normal workflows.

## Gate 14 — agent interface

Required:

- agent uses versioned public operations;
- no terminal parsing or hidden privileges;
- side-effect boundaries are explicit;
- proposed semantic changes can be validated before mutation;
- plans and explanations are structured;
- invalid requests fail safely;
- agent respects managed ownership;
- final report identifies custom work and unmodeled requirements.

Failure condition:

Agent integration bypasses the lifecycle used by human clients.

## Gate 15 — effectiveness

Required before broad product claims:

- comparison with conventional specialized tools;
- comparison with direct AI repository editing;
- repeated real-project tasks;
- total time including correction and review;
- omission and inconsistency counts;
- runtime and pack maintenance costs;
- migration and upgrade evidence;
- published unfavorable cases and limitations.

Failure condition:

Claims rely on a toy greenfield demonstration or generated line count.

## Release classifications

### Experimental

Contracts may change. Used to learn, not to promise compatibility.

### Preview

Core contracts are coherent; reference workflow works; some compatibility, platform, or adoption evidence remains incomplete.

### Stable subsystem

A bounded package or contract has passed its relevant gates and follows published compatibility policy.

### Stable product line

The connected package family and reference pack workflow pass all applicable gates from installed artifacts on the exact release commit.

### Production-proven

In addition to stable release gates, several real projects have evolved safely over time and published operational evidence exists.

## Release evidence record

Every release report should include:

```text
release identity and exact commit
package and behavior versions
supported platforms
normative contract versions
commands executed
test and generated-target results
reference project digests
known failures/skips
compatibility changes
security/trust changes
migration instructions
claim maturity changes
```

## Final release rule

When evidence conflicts with schedule, narrow the release claim or scope. Do not weaken determinism, output safety, semantic authority, or compatibility gates to preserve a date.
