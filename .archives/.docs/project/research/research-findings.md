# Research findings: Codepot in the modern engineering landscape

## Scope

This document summarizes the external evidence used to assess Codepot. It focuses on whether the industry needs deterministic software derivation, where comparable tools already succeed, and which claims remain unproven.

Detailed references are listed in [`sources.md`](sources.md).

## Finding 1 — AI increases the need for engineering control surfaces

The current developer-tool market is not short of code-writing capability. The harder problem is turning fast local output into reliable system-level delivery.

DORA’s 2025 research describes AI as an amplifier: strong organizations can convert it into better performance, while weak systems amplify bottlenecks and disorder. DORA’s platform-engineering guidance reports widespread internal-platform adoption in its research population and emphasizes automation, self-service, repeatability, governance, and clear feedback.

The implication for Codepot is direct:

```text
AI model capability
        ≠
reliable software delivery
```

A derivation runtime can add value by constraining repetitive implementation, validating relationships, exposing a plan, and applying changes through managed pathways.

### What this supports

- runtime operations shared by humans and agents;
- complete planning before mutation;
- machine-readable diagnostics;
- compatibility and policy checks;
- repeatable golden paths;
- traceability between intent and output.

### What this does not prove

- that Codepot improves productivity;
- that developers will author canonical contracts;
- that a broad semantic kernel is preferable to several narrow schemas;
- that AI agents will choose Codepot over direct repository edits.

Those outcomes require controlled project experiments.

## Finding 2 — developer adoption of AI is high, but trust is weak

The 2025 Stack Overflow Developer Survey reports high AI use or planned use, but more respondents distrust output accuracy than trust it. Common frustrations include solutions that are almost correct and time spent debugging generated code. Accuracy, security, and privacy concerns are especially strong around agents.

This is the clearest modern argument for Codepot’s agent role. An agent should not need to improvise every DTO, migration, SDK model, route type, and documentation update independently. A typed semantic patch and deterministic artifact plan can reduce inconsistency and make review more focused.

However, Codepot must not use these survey findings to claim that developers want a new DSL. The same survey ranks usability, cost, alternatives, security, and efficiency as major technology-selection factors. A trustworthy architecture with poor usability will still be rejected.

## Finding 3 — specification-driven AI workflows are emerging

GitHub Spec Kit promotes living specifications as the shared source of truth for coding agents. It organizes work around specification, planning, tasks, implementation, and validation instead of one-shot prompting.

Codepot can occupy a more mechanical layer below product specifications:

```text
product specification
        ↓ interpretation
canonical semantic proposal
        ↓ deterministic validation
artifact plan and generation
```

Natural-language specifications should not be treated as the canonical Dryv IR. They are richer but ambiguous. The IR should contain only meaning that the runtime can type, validate, version, compare, select, and expose to packs.

## Finding 4 — schema governance succeeds when compatibility semantics are bounded

Buf’s breaking-change detection demonstrates several relevant principles:

- compare the current schema with an explicit prior state;
- use deterministic rules;
- distinguish generated-source compatibility from wire compatibility;
- allow policy to decide whether an identified break is acceptable;
- integrate checks throughout development and review;
- avoid pretending that arbitrary custom options have universally knowable compatibility semantics.

Dryv should implement compatibility with the same discipline. Every approved kernel concept should define its compatibility behavior. Unknown extensions may be preserved, but they should not silently receive fabricated compatibility guarantees.

Codepot needs at least four compatibility views:

1. semantic source compatibility;
2. canonical transport and IR-version compatibility;
3. pack/runtime/plugin compatibility;
4. generated consumer or artifact compatibility where the target pack can declare it.

## Finding 5 — focused semantic models can support durable code generation

Smithy validates the broad architectural idea of a semantic model separated from target-language concerns. Its code-generation guidance emphasizes reusable generator structures, symbols, dependency handling, and separation between generic generation and provider-specific behavior.

Codepot’s architecture has a similar strength:

- canonical software meaning remains target-neutral;
- target plugins provide facts and validation;
- packs author target syntax;
- dependencies and symbols are planned explicitly.

The caution is equally important. Smithy is focused on service modeling. Codepot’s broader application-system scope must be earned concept by concept. “Smithy works” is not proof that a universal application IR will work.

## Finding 6 — scaffolding and golden paths are established needs

Backstage Software Templates let organizations load skeletons, collect inputs, execute steps, and publish new components. This demonstrates demand for self-service organizational standards and reusable project patterns.

Codepot should not duplicate Backstage’s portal role. Its stronger lifecycle proposition is continuous semantic derivation:

```text
Backstage-style scaffolding
    create a component from a template

Codepot-style derivation
    repeatedly evolve connected artifacts from canonical meaning
```

A platform team could use both. A portal or catalog may invoke Codepot runtime operations, while Dryv continues to govern regeneration after project creation.

## Finding 7 — interface generators already cover a large part of the market

OpenAPI Generator supports a broad catalog of clients, servers, documentation outputs, and schemas. Protocol Buffers, GraphQL tools, ORM generators, and framework CLIs also handle common repetitive work.

Therefore, Codepot cannot justify itself by saying only:

> We generate many languages from a schema.

Its stronger differentiation must be:

- one broader but governed semantic contract;
- coordinated output from several packs;
- explicit artifact dependencies;
- compatibility across semantic evolution;
- managed ownership and safe regeneration;
- explainable selection and binding;
- bidirectional traceability;
- the same operations for humans and agents.

Without those capabilities, teams should use the simpler specialized generator.

## Finding 8 — AI productivity is context-dependent

METR’s early-2025 randomized study found a slowdown for experienced developers using the studied AI tools on familiar open-source repositories, despite expected speedups. METR later stated that newer systems likely provide more benefit but that updated measurement was affected by selection bias and other methodological difficulties.

The correct conclusion is not “AI slows developers.” It is:

- productivity cannot be inferred from model capability alone;
- perceived speed is not enough;
- repository familiarity, task type, review, and correction cost matter;
- modern tools require ongoing measurement.

Codepot must therefore test end-to-end change workflows rather than counting generated files or asking users whether the system feels powerful.

## Finding 9 — model-driven and DSL approaches can work, but adoption is conditional

Model-driven engineering and domain-specific languages have repeatedly shown potential to reduce accidental complexity and improve reuse. Empirical studies also identify recurring adoption constraints:

- learning cost;
- tool quality;
- flexibility;
- integration with ordinary workflows;
- readability of generated artifacts;
- organizational support;
- training and documentation;
- the cost of maintaining the model and generators.

The current AI era changes but does not remove these constraints. Agents may reduce authoring cost, yet a low-resource or unfamiliar DSL may itself be harder for a general model to use reliably.

Codepot should therefore expose:

- a formal machine-readable IR schema;
- structured edit and patch operations;
- inspectable examples;
- stable diagnostic codes;
- public selector and context catalogs;
- generated plans that agents can validate;
- authoring frontends in familiar languages;
- canonical transport for portability.

It should not depend on agents learning undocumented conventions.

## Finding 10 — determinism is necessary but not sufficient

Determinism provides reproducibility and makes defects repeatable. It does not guarantee that a template is correct, that a semantic contract represents the business accurately, or that generated architecture is appropriate.

A high-quality Codepot workflow needs multiple layers:

```text
semantic validation
compatibility validation
pack conformance
artifact-plan validation
render determinism
generated-project verification
human review
runtime and production testing
```

The project should avoid marketing “deterministic” as a synonym for “correct.”

## Finding 11 — explainability can be a practical differentiator

Many generators can tell users that a file was produced. Fewer can explain:

- which semantic item selected the template;
- why the item matched;
- which context values were provided;
- which generated providers satisfied imports;
- why the path was chosen;
- which binding changed the result;
- which pack and version owned the artifact;
- what will happen if the semantic item changes or disappears.

This explanation graph can become one of Codepot’s strongest features for review, debugging, and AI collaboration. It should be a runtime artifact, not reconstructed from logs.

## Finding 12 — Codepot’s opportunity is a category intersection

Codepot sits at the intersection of:

```text
model-driven engineering
schema and API governance
platform engineering
code generation
internal developer platforms
AI-agent tooling
software supply-chain controls
```

No single adjacent tool proves the full Codepot design. The opportunity exists because most tools own only one portion:

| Approach | Strongest ownership | Typical limitation relative to Codepot |
|---|---|---|
| OpenAPI Generator | API clients/servers/docs | API-centered semantics and limited cross-artifact ownership |
| Protobuf + Buf | wire contracts, generated stubs, compatibility | intentionally focused semantic domain |
| Smithy | service semantic model and codegen | primarily service/API modeling |
| Backstage templates | project scaffolding and golden paths | creation-oriented rather than canonical ongoing derivation |
| ORM generators | persistence models and migrations | storage-centered semantics |
| AI coding agents | flexible repository modification | probabilistic consistency and weak generated ownership |
| Custom scripts | local automation | limited portability, governance, and shared contracts |

Codepot’s value is the coordinated whole. Its risk is that the whole becomes too large to understand or maintain.

## Research-backed design implications

The external evidence supports these decisions:

1. Treat Codepot as an internal-platform capability, not only a code generator.
2. Make feedback and explanation immediate and clear.
3. Keep compatibility policies explicit and bounded.
4. Preserve a target-neutral semantic core.
5. Prefer known typed concepts over arbitrary extension semantics.
6. Use conventional Git and package distribution instead of proprietary credential systems.
7. Measure lifecycle outcomes, not code volume.
8. Keep the initial product scope narrower than the eventual architecture.
9. Give agents constrained runtime operations rather than privileged repository magic.
10. Make usability, documentation, and migration equal priorities with kernel design.

## What remains unknown

Research does not answer these Codepot-specific questions:

- Can ordinary developers author the contract faster than they can maintain conventional code and schemas?
- Can pack authors support framework evolution at acceptable cost?
- Does the closed kernel cover enough real software without semantic escape hatches?
- Can several authoring languages produce behaviorally equivalent contracts?
- Can generated and handwritten ownership remain comfortable over years?
- Will teams trust managed regeneration in existing repositories?
- Will AI agents use the runtime correctly when direct editing is available?
- Can a pack ecosystem maintain quality and security?
- Can Codepot outperform specialized tools for a meaningful set of workflows?

These are engineering research questions and should be tracked through the validation program, not resolved through architectural confidence.
