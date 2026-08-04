# Codepot usability and adoption

## Principle

A correct architecture that ordinary teams cannot understand will not improve software engineering. Codepot must be designed as a developer product, a pack-author product, and an agent tool—not merely as a semantic kernel.

The usability objective is:

> A user should be able to predict what Codepot will read, select, generate, change, preserve, and execute before any files are modified.

## Primary users

### Application developer

Needs to:

- understand the authored software contract;
- select approved packs;
- preview changes;
- extend generated output safely;
- diagnose why an artifact changed;
- evolve the contract without breaking consumers accidentally.

The application developer should not need to understand runtime internals, plugin discovery, graph algorithms, or template-engine implementation.

### Platform engineer

Needs to:

- define organizational golden paths;
- maintain packs and bindings;
- certify compatibility;
- govern remote pack sources and commands;
- measure reuse and failures;
- support several project teams without forking the runtime.

### Pack author

Needs to:

- discover available selectors and context values;
- create templates and static files;
- declare symbols and dependencies;
- validate packs independently;
- simulate realistic contracts;
- understand portability and compatibility failures;
- publish packs through ordinary version-control and package workflows.

### Authoring-frontend implementer

Needs to:

- implement the public canonical contract exactly;
- reuse core validation and transport;
- prove semantic equivalence through conformance fixtures;
- provide language-native ergonomics without adding semantics.

### AI agent

Needs to:

- inspect typed runtime capabilities;
- read and patch canonical meaning through bounded operations;
- obtain stable diagnostics and plans;
- avoid interactive prompts;
- identify generated ownership;
- report traceable results.

### Reviewer and operator

Needs to:

- see semantic intent and compatibility impact;
- inspect files and commands before execution;
- audit which pack and source produced an artifact;
- reproduce generation;
- roll back or recover safely.

## The default workflow

The command names may differ by frontend, but the mental model should remain:

```text
inspect
    understand contract, plugins, packs, lock, and state

validate
    check every contract without side effects

plan
    calculate exact artifacts, changes, dependencies, and commands

review
    approve policy decisions and the mutation boundary

generate
    render and commit through managed output

verify
    run declared generated-project checks

trace
    explain semantic-to-artifact and artifact-to-semantic relationships
```

A user should never need to run `generate` merely to discover a plan error that could have been reported earlier.

## First-use experience

A successful first-use path should fit on one screen of documentation:

1. install a runtime distribution and required plugins;
2. point to an authored or serialized contract;
3. add one local pack;
4. run validation;
5. view the plan;
6. generate into an empty destination;
7. inspect ownership state and trace one artifact;
8. change one field and repeat.

The example must demonstrate evolution, not only creation.

## Configuration usability

### Project configuration

`dryv.yaml` should be readable as an orchestration map. It should not duplicate pack internals.

Every pack instance should make visible:

- instance identity;
- source and immutable resolution status;
- semantic input;
- output root;
- options;
- bindings;
- project-owned overrides;
- command policy.

### Pack configuration

`DryvPack.yaml` should be smaller than the behavior it enables. Safe facts should be inferred from the filesystem; non-inferable behavior should be declared.

The manifest must not require:

- registering every literal template;
- repeating output paths that are identical to template paths;
- restating every static file;
- encoding framework syntax;
- arbitrary graph queries;
- undocumented helper variables.

### Schemas and editor support

Project and pack configuration should have machine-readable schemas, completion, validation, hover documentation, and precise source locations. The same schemas should be used by editors, CLI validation, and agent tools.

## Diagnostic design

A diagnostic should include:

```text
stable code
severity
summary
explanation
source location
semantic identity
pack/template/plugin identity when relevant
related locations
suggested remediation
machine-readable details
```

Diagnostics should distinguish:

- authoring errors;
- canonical semantic errors;
- compatibility violations;
- pack contract errors;
- selection and context errors;
- dependency and symbol errors;
- path and collision errors;
- trust and approval errors;
- render errors;
- write/transaction errors;
- generated-project verification failures.

Raw language exceptions or template-engine stack traces may appear as debug details, not as the primary user explanation.

## Plan presentation

A useful plan begins with decisions, not internal nodes:

```text
Project: ticketing
Contract digest: ...
Packs: 4
Artifacts: 37 add, 12 update, 2 remove, 19 unchanged
Commands: 2 pending approval
Compatibility: 1 warning, 0 blocked
Conflicts: 0
```

Users can then expand:

- by pack;
- by semantic group;
- by artifact action;
- by compatibility class;
- by command;
- by source semantic change.

Machine output should expose the complete graph with stable IDs. Human output should not dump the graph by default.

## Explanation experience

The system should answer ordinary questions directly:

- Why was this file generated?
- Why was this template selected?
- Why was a template skipped?
- Where did this name come from?
- Which option or binding changed this result?
- Which generated artifact provides this import?
- What semantic item owns this artifact?
- What will be removed if I continue?
- Why is this change considered breaking?
- Why can this file not be overwritten?
- Which source and commit supplied this pack?

Explanations should be queryable before and after generation.

## Safe customization experience

Each pack should document:

- artifacts fully owned by generation;
- extension interfaces and handwritten neighbors;
- bindings expected from the project;
- files safe to replace or override;
- files that must never be edited;
- how to add custom behavior;
- how to upgrade the pack;
- how to stop using the pack.

A generated header alone is not sufficient. Ownership state and runtime inspection must remain authoritative.

## Progressive disclosure

### Beginner surface

- one contract;
- one local pack;
- validate, plan, generate;
- no remote commands;
- simple filesystem-derived templates.

### Intermediate surface

- several packs;
- options and bindings;
- explicit imports/exports;
- Git sources and lock;
- managed stale cleanup;
- generated-target verification.

### Advanced surface

- cross-pack artifact dependencies;
- policy and approval management;
- custom source/target/engine plugins;
- compatibility baselines;
- impact analysis;
- agent/server integration;
- performance and incremental operation.

Advanced capability should not make the beginner path verbose.

## Pack-author tooling

A pack development environment should provide:

- manifest validation;
- template and static-file discovery preview;
- selector catalog browsing;
- context schema inspection;
- fixture execution;
- expected artifact snapshots;
- symbol and dependency visualization;
- path portability checks;
- sandbox violations;
- deterministic rerun checks;
- pack compatibility checks;
- documentation generation from declared options, bindings, selections, and symbols.

A pack author should be able to debug a pack without installing it into a real application repository.

## Agent usability

Agent-facing operations should be explicit and small:

- inspect runtime and project;
- obtain contract schema and selected semantic slices;
- validate a proposed canonical patch;
- compare contracts;
- produce a plan;
- explain plan nodes;
- generate to memory or files according to policy;
- retrieve verification and trace reports.

Agents should not receive an operation called “fix everything.” They should compose the same inspectable lifecycle used by humans.

Structured results need:

- stable operation kinds;
- versioned schemas;
- deterministic pagination/order;
- diagnostic codes;
- explicit side-effect declarations;
- cancellation and timeout semantics;
- idempotency where applicable;
- no ANSI or prose-only machine output.

## Adoption strategy

### Start with internal use

The most realistic first adopters are teams already suffering from repeated cross-artifact maintenance. Use Codepot in real Codepot-related or Alidantech projects before asking external teams to trust it.

### Sell the change, not the architecture

A demonstration should show:

```text
before:
change one concept in many places, discover omissions during review or runtime

after:
change canonical meaning, inspect compatibility and plan, regenerate safely
```

Do not lead with metamodel terminology.

### Provide one excellent pack family

A small coherent family is more persuasive than many incomplete targets. The first pack family should produce several connected artifacts and survive repeated evolution.

### Preserve normal tools

Generated projects should continue to use normal compilers, test runners, formatters, IDEs, package managers, and Git. Codepot should integrate with software engineering rather than create a sealed environment.

### Make exit possible

Adoption is safer when teams can:

- inspect canonical transport;
- own pack source;
- pin versions;
- retain generated files;
- stop generation deliberately;
- migrate to another pack;
- continue with handwritten code.

Lock-in fear will otherwise outweigh the productivity promise.

## Adoption blockers to monitor

- authoring feels more verbose than direct code;
- pack errors require runtime expertise;
- generation plans are too large to review;
- generated files are not idiomatic;
- framework upgrades lag;
- custom behavior requires editing managed files;
- semantic concepts do not match team vocabulary;
- remote pack trust is unclear;
- configuration becomes another programming language;
- users cannot distinguish Codepot, Dryv, packages, and historical tools;
- agent integration is marketed before human workflows are reliable.

## Usability success metrics

Measure:

- time to first successful generation;
- time to understand a plan;
- percentage of errors resolved from the first diagnostic;
- number of runtime-source lookups needed by pack authors;
- pack creation time for a defined reference task;
- time to complete a real semantic evolution;
- manual edits to generated files;
- user prediction accuracy before generation;
- onboarding completion without maintainer help;
- agent retries caused by unclear diagnostics;
- adoption retention after the first project.

## Usability release gate

Before calling the system generally usable, a developer unfamiliar with the implementation should be able to:

1. read the contract;
2. configure two packs;
3. understand a plan;
4. generate a connected project;
5. add a field and an operation;
6. handle one compatibility warning;
7. recover from one manual-edit conflict;
8. trace a generated file;
9. explain where custom code belongs;
10. repeat the output on another machine.

Success must be observed, not inferred from documentation completeness.
