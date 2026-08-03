# Codepot cookbook: crafting a compatible system in any language

## How to use this cookbook

This is a recipe for implementing Codepot’s architecture without depending on Python, TypeScript, Rust, or any particular framework. A team may choose different technologies, but the artifacts, boundaries, and acceptance questions should remain equivalent.

Each recipe contains:

- **Goal** — the capability being created;
- **Inputs** — decisions or artifacts that must already exist;
- **Method** — architecture steps;
- **Output** — the public artifact produced;
- **Checks** — evidence that the recipe is complete;
- **Do not** — common shortcuts that weaken the design.

## Recipe 1 — write the product charter

### Goal

Prevent the implementation from becoming a universal generator.

### Inputs

- two real projects;
- examples of repeated cross-artifact changes;
- current manual/AI workflows;
- intended users.

### Method

1. Describe the problem in one sentence.
2. List repeated artifacts that represent the same meaning.
3. Separate portable meaning from target implementation.
4. Identify work that must remain handwritten.
5. Define first packs and first authoring route.
6. Define measurable success and kill criteria.
7. Publish anti-goals.

### Output

A short product contract that every subsystem can reference.

### Checks

- A developer can explain why Codepot is preferable to OpenAPI plus scripts for the chosen case.
- The charter identifies cases where Codepot should not be used.

### Do not

- promise every language and framework;
- define success as lines generated;
- choose features before selecting real evolution tasks.

## Recipe 2 — identify canonical semantic concepts

### Goal

Create the smallest target-neutral model that supports the reference workflows.

### Inputs

- product charter;
- examples from several target artifacts;
- historical Codepot lessons.

### Method

For every candidate concept, ask:

1. Does it have the same meaning across targets?
2. Must the runtime validate or compare it?
3. Must packs select it?
4. Must impact and trace include it?
5. Can it be declared without target executable code?
6. Can at least two outputs use it differently?

Classify the concept as:

- kernel object;
- kernel relationship;
- approved facet/value;
- pack option;
- project binding;
- namespaced tag;
- guidance;
- bounded raw/provenance;
- handwritten implementation concern.

### Output

A semantic inventory with explicit inclusion and exclusion rationale.

### Checks

- No concept is named only after one framework construct.
- Every included concept has identity, containment, references, ordering, and compatibility rules.

### Do not

- add generic metadata bags;
- treat a schema as an automatic entity, endpoint, form, or event;
- model emitted classes and folders as semantic truth.

## Recipe 3 — define stable semantic identity

### Goal

Allow contracts to evolve without confusing names and locations with identity.

### Inputs

- semantic inventory;
- source provenance needs;
- compatibility scenarios.

### Method

1. Define contract, group, and item identity scopes.
2. Decide how explicit and derived IDs coexist.
3. Define deterministic derived-ID inputs.
4. Separate identity from display name, qualified name, source path, and generated path.
5. Define rename, move, copy, merge, and split semantics.
6. Preserve origin and derivation provenance.
7. Define collision diagnostics.

### Output

A stable identity specification.

### Checks

- Reordering declarations does not change IDs.
- An intentional rename can preserve identity.
- Two independent authoring implementations assign equivalent identities.

### Do not

- use object memory addresses;
- use generated output paths as semantic IDs;
- change identity because a source file moved.

## Recipe 4 — define canonical immutable IR

### Goal

Create the only portable semantic authority.

### Inputs

- semantic inventory;
- identity rules;
- version policy.

### Method

1. Define immutable values for every object and relation.
2. Use typed references rather than arbitrary strings where possible.
3. Define explicit optionality and presence.
4. Define deterministic collection ordering.
5. Separate declared facts from computed/effective facts.
6. Include source provenance without source-language objects.
7. Bound extensions and raw data.
8. Define canonical behavior version and schema version.

### Output

A public Runtime IR contract independent of authoring and generation.

### Checks

- IR contains no builder, renderer, filesystem, plugin, CLI, or target-library object.
- The complete contract can exist in memory without serialization.
- Every value is deterministic and inspectable.

### Do not

- expose mutable collections;
- include callables;
- store framework classes;
- create separate “author IR” and “runtime IR” semantic models.

## Recipe 5 — define canonical transport

### Goal

Share, review, cache, and load the same Runtime IR portably.

### Inputs

- immutable IR;
- ordering rules;
- version policy.

### Method

1. Define canonical property names and value encodings.
2. Normalize order and omission rules.
3. Define JSON and optionally YAML representations.
4. Preserve enough provenance for review and diagnostics.
5. Validate on load.
6. Reject unknown behavior versions according to policy.
7. Define canonical digest input.
8. Add round-trip and malformed-input fixtures.
9. Add indexed/lazy representations only as infrastructure views.

### Output

Runtime-owned serializers and loaders with a stable transport schema.

### Checks

- serialize-load-serialize is canonical;
- equivalent contracts produce the same digest;
- YAML parsing cannot change meaning through ambiguous scalar coercion;
- unknown fields follow an explicit policy.

### Do not

- let authoring own serialization;
- serialize frontend builders;
- make JSONL another semantic authority;
- include nondeterministic timestamps in canonical digests.

## Recipe 6 — build validation and diagnostics

### Goal

Make invalid meaning fail before planning.

### Inputs

- IR contracts;
- reference and containment rules;
- compatibility model.

### Method

Validate in ordered stages:

1. transport and structural validity;
2. identity uniqueness;
3. reference existence and kind;
4. containment and ownership;
5. schema and constraint consistency;
6. operation/facet consistency;
7. policy, event, storage, view, and workflow relationships;
8. cycles where prohibited;
9. naming and portability;
10. extension bounds;
11. compatibility when a baseline is supplied.

Every failure receives a stable diagnostic code, severity, locations, related identities, explanation, and remediation.

### Output

A pure validation result and diagnostic catalog.

### Checks

- ordinary user errors do not escape as raw exceptions;
- diagnostic ordering is stable;
- the same invalid contract produces equivalent results across frontends;
- warnings never silently change behavior.

### Do not

- fix semantic errors automatically;
- rely on message text as the machine contract;
- continue into generation with a contract missing required references.

## Recipe 7 — define compatibility rules

### Goal

Identify whether semantic evolution can break consumers.

### Inputs

- previous and current canonical contracts;
- stable identity;
- known consumer categories.

### Method

1. Match items by stable identity.
2. classify additions, removals, renames, moves, and modifications.
3. define compatibility rules per object and relation;
4. distinguish source, transport, wire, storage, and generated-consumer consequences where knowable;
5. produce affected-consumer and affected-artifact estimates;
6. separate detected break from project policy;
7. support explicit reviewed waivers;
8. include compatibility behavior version in evidence.

### Output

A structured compatibility report.

### Checks

- removal and constraint tightening are never silently ignored;
- unknown extension semantics are labeled unknown;
- policy can block, warn, or allow without altering detection.

### Do not

- claim universal compatibility for target-specific code;
- infer identity only from names;
- hide deliberate breaking changes behind version increments.

## Recipe 8 — implement an authoring frontend

### Goal

Provide familiar, concise declarations that compile into canonical IR.

### Inputs

- public IR schema;
- conformance corpus;
- diagnostics contract.

### Method

1. Define author-session ownership and lifecycle.
2. Return typed immutable references from declarations.
3. collect declarations without global mutable registries.
4. freeze the session before compilation.
5. validate frontend-native declarations.
6. assign stable identities.
7. resolve references in deterministic passes.
8. expand explicit reusable composition and derivations.
9. construct only public IR values.
10. run core validation.
11. return contract plus diagnostics.

### Output

A language-native authoring package whose only semantic product is canonical IR.

### Checks

- conformance fixtures match canonical expected output;
- forward and wrong-kind references produce structured errors;
- builder order does not affect output;
- no target pack or output path is visible to authoring.

### Do not

- generate files;
- serialize independently;
- preserve language runtime objects in IR;
- invent private semantic conveniences.

## Recipe 9 — define project usage configuration

### Goal

Connect semantic inputs, packs, options, bindings, and outputs simply.

### Inputs

- contract-provider interface;
- pack-source interface;
- output policy.

### Method

Define project configuration containing:

- project identity;
- semantic contract source;
- pack instances;
- direct local/Git pack sources;
- output roots;
- typed options;
- public bindings;
- controlled overrides;
- lock/frozen policy;
- command/trust policy.

### Output

A project configuration that can be validated without generation.

### Checks

- configuration answers what is active and where it writes;
- it contains no semantic object definitions;
- two pack instances can use the same pack with different outputs/options;
- all source identities can be locked.

### Do not

- place template definitions in project configuration;
- create a second selector language;
- hide output roots in environment variables without plan visibility.

## Recipe 10 — define a pack

### Goal

Package reusable emission behavior portably.

### Inputs

- selector catalog;
- context schemas;
- path and naming contracts;
- engine/target adapter contracts.

### Method

1. Give the pack stable identity and compatibility requirements.
2. Organize templates and static files through filesystem conventions.
3. declare only dynamic selection folders and non-inferable behavior.
4. define typed options and bindings.
5. declare generated symbols and dependencies.
6. declare commands and approvals.
7. provide fixtures and expected artifacts.
8. document ownership and extension patterns.
9. provide upgrade and exit guidance.

### Output

A pack that is independently inspectable and testable.

### Checks

- all selected contexts are documented;
- every dynamic destination is deterministically calculable;
- dependencies resolve without rendered-source inspection;
- literal files require no redundant manifest entry;
- pack behavior is portable across projects.

### Do not

- access private runtime objects;
- use arbitrary graph traversal;
- rely on a global template registry;
- execute commands during discovery or validation.

## Recipe 11 — define selectors and contexts

### Goal

Expose canonical meaning to packs safely and predictably.

### Inputs

- semantic topology;
- recurring pack use cases;
- ordering rules.

### Method

1. Define fixed root-first selectors.
2. specify selected item type and deterministic ordering.
3. provide singular and collection context forms.
4. include parent ownership and common roots consistently.
5. define names and computed facts through typed descriptors.
6. version context schemas.
7. document every property.
8. record selection reasons during planning.

### Output

A public selector and template-context catalog.

### Checks

- packs do not reconstruct ownership from names;
- the same selector result is independent of source frontend;
- no context contains mutable runtime objects or secrets;
- values needed by templates are serializable for inspection.

### Do not

- expose the entire contract by default;
- let packs invent selectors;
- add target syntax to context values.

## Recipe 12 — define path and naming expressions

### Goal

Calculate portable output paths without hidden filename magic.

### Inputs

- names/descriptors;
- selected contexts;
- target validation facts.

### Method

1. Define a small expression grammar.
2. separate literals from dynamic expressions clearly.
3. expose one naming vocabulary with casing and number transforms.
4. normalize internal paths to portable separators.
5. validate each segment and final destination.
6. detect traversal, reserved names, and case collisions.
7. include path evaluation steps in explanation artifacts.
8. compile source template paths into path expressions deterministically.

### Output

A safe, explainable destination descriptor for every planned artifact.

### Checks

- path results do not depend on the host OS;
- literal framework route brackets remain literal;
- semantic records do not pretend to own generated file paths;
- two artifacts cannot silently resolve to the same normalized destination.

### Do not

- allow arbitrary host-language code in path expressions;
- concatenate unvalidated semantic text into paths;
- infer paths at render time.

## Recipe 13 — plan artifacts

### Goal

Produce the complete immutable generation plan.

### Inputs

- valid canonical contract;
- valid project configuration;
- resolved and validated packs/plugins;
- optional previous contract/lock/state.

### Method

1. resolve semantic input and behavior identities;
2. evaluate selectors in stable order;
3. create stable invocation identities;
4. compile destinations;
5. register static and dynamic artifacts;
6. register symbols and generated dependencies;
7. resolve providers and target module/path facts;
8. apply options and bindings;
9. calculate compatibility and impact;
10. compare with ownership state;
11. register commands and approvals;
12. validate collisions, cycles, ambiguity, trust, and capabilities;
13. create explanation edges;
14. freeze and digest the plan.

### Output

An immutable plan suitable for review, rendering, and writing.

### Checks

- renderers need no discovery;
- writers need no semantic decisions;
- invalid plans contain no executable side-effect authorization;
- plan serialization is stable;
- dry run presents this exact plan.

### Do not

- render to discover imports;
- write to detect collisions;
- let template order establish dependencies;
- automatically choose an ambiguous provider.

## Recipe 14 — render prepared contexts

### Goal

Turn valid artifact plans into in-memory bytes deterministically.

### Inputs

- valid frozen plan;
- resolved template/static content;
- engine and target capabilities.

### Method

1. verify plan and behavior digests;
2. prepare immutable bounded contexts;
3. render through the selected sandboxed engine;
4. copy static/binary content exactly;
5. normalize only explicitly governed output behavior;
6. calculate content digests;
7. capture structured diagnostics and template dependencies;
8. return in-memory artifacts.

### Output

A rendered-generation artifact with no filesystem mutation.

### Checks

- rerendering produces identical bytes;
- renderer cannot read arbitrary project files or environment secrets;
- target syntax comes only from pack content;
- each rendered artifact maps to one plan identity.

### Do not

- allow renderers to change destinations;
- run formatters or commands during render;
- pass mutable builders or plugin objects into templates.

## Recipe 15 — commit managed output

### Goal

Apply rendered artifacts safely and transactionally.

### Inputs

- valid plan;
- rendered artifacts;
- previous ownership state;
- approved command policy.

### Method

1. lock project/output scope.
2. inspect current filesystem and content digests.
3. classify additions, updates, unchanged, stale, unmanaged collisions, and modified managed files.
4. fail or require explicit resolution for unsafe cases.
5. stage the complete write/delete set.
6. validate staged output.
7. atomically commit artifacts where possible.
8. commit new ownership state.
9. run separately approved post-generation commands only at their declared stage.
10. record result and trace.
11. roll back on failure according to transaction policy.

### Output

A generation result and updated managed state.

### Checks

- failure injection leaves the prior state valid;
- modified managed files are never silently lost;
- stale deletion is conservative;
- cancellation is safe;
- concurrent runs cannot interleave.

### Do not

- delete by glob without ownership proof;
- write state before files;
- treat a generated header as the only ownership record;
- mix command output with canonical runtime result data.

## Recipe 16 — explain and trace

### Goal

Make every derivation reviewable and diagnosable.

### Inputs

- canonical contract;
- plan;
- render result;
- ownership state;
- compatibility report.

### Method

Create stable edges among:

```text
source declaration/provenance
semantic item
selector invocation
pack instance
selection/template/static origin
option/binding
artifact plan
symbol/provider dependency
rendered artifact
managed file
verification result
```

Expose queries in both directions and include selection/skip/path/provider reasoning.

### Output

A machine-readable explanation and trace graph with human views.

### Checks

- every managed artifact has semantic and pack provenance;
- every selected semantic item lists affected artifacts;
- skipped templates have explainable reasons;
- trace survives process exit through state or reproducible plan data.

### Do not

- reconstruct trace from log messages;
- expose secrets or credentials;
- present internal call stacks as product explanations.

## Recipe 17 — lock and trust sources

### Goal

Make generation reproducible and remote behavior auditable.

### Inputs

- project configuration;
- source/provider interfaces;
- trust policy.

### Method

1. resolve mutable source references.
2. identify immutable commit/version and subdirectory.
3. calculate content and manifest digests.
4. record plugin/engine/target behavior identities.
5. record required capabilities and commands.
6. keep credentials outside all stored artifacts.
7. require approval for untrusted remote commands.
8. verify cache contents against lock.
9. expose update and frozen modes.

### Output

An immutable project dependency lock and trust report.

### Checks

- moving a branch does not alter frozen generation;
- cache corruption is detected;
- locks contain no credentials;
- exact pack source appears in plans and traces.

### Do not

- use mutable marketplace aliases as runtime identity;
- trust a package name without source/digest verification;
- execute pack code merely to inspect metadata.

## Recipe 18 — design public runtime operations

### Goal

Let every frontend use one behavior contract.

### Inputs

- validation, planning, rendering, writing, inspection, and trace services.

### Method

Define versioned request/result operations such as:

- inspect runtime/project/contract/pack/plugin/lock/state;
- validate contract/project/pack/plugin;
- compare contracts and compatibility;
- resolve/update lock;
- plan generation;
- explain selection/artifact/dependency;
- generate to memory/archive/files;
- verify generated project;
- query trace;
- manage approvals through trusted policy.

Each operation declares side effects, cancellation, timeout, idempotency, diagnostics, and result schema.

### Output

A frontend-neutral runtime facade.

### Checks

- CLI imports only public runtime contracts;
- machine clients need no terminal parsing;
- non-interactive operations never prompt;
- human confirmation cannot change the calculated plan.

### Do not

- put formatting and color in runtime data;
- give the CLI unique generation behavior;
- create agent-only semantic shortcuts.

## Recipe 19 — build the first pack family

### Goal

Prove multi-artifact value.

### Inputs

- stable minimum runtime;
- two reference projects;
- target toolchains.

### Method

Build a coherent family that derives:

1. service/API boundary artifacts;
2. storage/migration artifacts;
3. one SDK/client package;
4. documentation or inspection artifacts.

Connect them through explicit symbols and semantic dependencies. Provide extension points for handwritten business logic.

### Output

A real generated vertical slice.

### Checks

- all generated targets compile/analyze;
- API and SDK interoperate;
- storage change is validated;
- repeated semantic evolution remains safe;
- output is idiomatic and reviewable;
- same packs work in two projects.

### Do not

- build many shallow packs;
- generate custom algorithms;
- hand-edit managed output to make the demonstration pass.

## Recipe 20 — evaluate effectiveness

### Goal

Decide whether Codepot should expand.

### Inputs

- reference pack family;
- conventional and AI baselines;
- evolution task sequence.

### Method

Compare workflows using:

- time;
- omissions;
- inconsistencies;
- review effort;
- test failures;
- corrective iterations;
- agent token/tool cost;
- maintenance cost;
- user confidence;
- pack reuse;
- migration effort.

Include tasks where direct coding is expected to win.

### Output

An evidence report identifying strong, weak, and inappropriate use cases.

### Checks

- claims match measured scope;
- maintenance costs are included;
- limitations and failures are published;
- scope narrows when evidence demands it.

### Do not

- use toy CRUD generation as the only benchmark;
- count generated lines as productivity;
- rely only on developer perception;
- hide failed or unfavorable tasks.

## Final cookbook checklist

A compatible Codepot implementation is ready for serious evaluation when all answers are yes:

- Is there one closed canonical semantic contract?
- Can several sources produce it without changing meaning?
- Does the runtime own transport and compatibility?
- Can packs be understood without runtime internals?
- Are selectors and contexts fixed and documented?
- Is every artifact and dependency planned before rendering?
- Do templates own emitted syntax?
- Are writes managed, transactional, and reversible?
- Are Git sources locked immutably without stored credentials?
- Can every generated file be traced and explained?
- Can humans and agents use the same public operations?
- Do generated targets pass their own toolchains?
- Does repeated real-project evolution show net value?

If any foundational answer is no, add capability at that layer before expanding product breadth.
