# Codepot refinement and scope

## Purpose

Codepot’s primary architectural danger is not insufficient capability. It is allowing the semantic kernel, pack system, or usage configuration to absorb every software concern. This document defines how to refine the product without turning it into a universal programming language or a thin template-context wrapper.

## Product center

Codepot should remain centered on this capability:

> Represent stable software meaning canonically, then derive connected implementation artifacts deterministically through explicit reusable packs.

The product is not centered on:

- generating the maximum number of files;
- replacing all handwritten code;
- modeling framework internals;
- providing a new syntax for ordinary programming;
- automatically inventing architecture;
- hiding decisions behind smart defaults;
- serving as an AI chat interface.

## The semantic inclusion test

A concept belongs in canonical Runtime IR only when all of these are true:

1. **Meaning is stable across targets.** It is not merely a class, decorator, folder, framework lifecycle, or library call.
2. **The runtime must reason about it.** It affects validation, compatibility, selection, impact, traceability, or policy.
3. **It has explicit identity and relationships.** The concept can be referred to and compared without guessing from names.
4. **It can be represented declaratively.** It does not require arbitrary executable code to preserve its meaning.
5. **Several outputs can use it differently.** At least two realistic packs or inspections benefit from the same fact.
6. **Its boundaries can be documented.** Attachment, ordering, inheritance, provenance, and migration are knowable.
7. **Its cost is justified.** The benefit exceeds the permanent kernel, compatibility, documentation, and conformance burden.

Failure of one test usually means the concept belongs in a pack, binding, tag, guidance record, or handwritten implementation.

## What belongs in the kernel

The current direction is reasonable for stable concepts such as:

- contracts and groups;
- structural schemas and fields;
- constraints, optionality, nullability, defaults, and references;
- operations, inputs, outputs, failures, and effects;
- approved transport, access, trigger, execution, and event facets;
- policies and their declared/effective application;
- event declarations and occurrence relationships;
- storage mappings, keys, indexes, relations, and constraints;
- views as neutral interaction units;
- workflows, steps, transitions, decisions, waits, and compensation;
- semantic documentation, guidance, provenance, and stable names;
- explicit relationships needed for impact and traceability.

These concepts must remain structural and target-neutral.

## What belongs in packs

Packs should own implementation decisions such as:

- class versus interface versus type alias;
- controller, resolver, handler, repository, service, or use-case structure;
- framework annotations and decorators;
- ORM declarations and migration syntax;
- UI component trees and styling;
- routing-library syntax;
- validation-library syntax;
- dependency-injection setup;
- import/export statements;
- target-specific filenames and module layouts;
- framework configuration;
- code comments and generated documentation prose;
- testing framework conventions;
- infrastructure manifests and deployment syntax.

A pack may choose a recognizable generated vocabulary such as `Entity`, `DTO`, `Controller`, or `Widget`. Those terms must not become universal semantic objects solely because a pack emits them.

## What belongs in project bindings and options

Bindings connect portable pack needs to project-specific facts. Examples include:

- package/module roots;
- base classes or interfaces supplied by the project;
- authentication integration names;
- existing infrastructure resource identifiers;
- runtime library choices supported by the pack;
- project import aliases;
- environment-specific destinations;
- approved naming prefixes or namespaces.

Bindings must not redefine semantic relationships. A binding can say which project symbol satisfies a pack requirement; it cannot transform an operation into a different kind of behavior.

Options configure bounded pack choices. An option should:

- have a declared type and default;
- identify which selections or templates it influences;
- appear in the plan explanation;
- be included in behavior digests;
- avoid open-ended arbitrary dictionaries when a typed structure is possible.

## What belongs in guidance

Guidance can carry useful intent that humans, agents, or templates may inspect but that does not create behavior automatically. Categories may include:

- explanation;
- implementation advice;
- security considerations;
- persistence expectations;
- testing guidance;
- caching and performance notes;
- observability needs;
- UX and accessibility guidance;
- warnings and rationale.

Guidance must never be interpreted as a hidden semantic command. If a rule must be enforced, it needs a typed kernel fact or explicit policy.

## What belongs in tags

Namespaced tags are useful Boolean hints for bounded pack selection or organization:

```text
ui:data-table
repository:custom
orm:custom
docs:public
```

Tags should be:

- namespaced;
- immutable;
- unique and sorted;
- included in digests;
- documented by packs that consume them;
- incapable of carrying arbitrary values or relationships.

When several packs depend on the same tag meaning, that is evidence to evaluate a typed kernel addition.

## What should remain handwritten

Codepot should intentionally leave these areas primarily handwritten unless a narrow pack can derive a safe scaffold:

- complex domain algorithms;
- optimization and numerical methods;
- novel data structures;
- nuanced business decisions not represented canonically;
- performance-critical target-specific code;
- highly bespoke UI interaction and animation;
- one-off integrations with unstable external behavior;
- incident-specific operational logic;
- framework internals and advanced metaprogramming.

The correct architecture is often:

```text
Codepot-generated contracts, boundaries, adapters, and repeated structure
        +
handwritten algorithms and custom behavior
```

## Refine authoring without changing semantics

Each authoring frontend may use familiar language features and ergonomic helpers. It may:

- provide typed references;
- support reusable composition functions;
- expand explicit derivation recipes;
- infer declarations from supported language-native models;
- provide editor feedback;
- collect source spans and provenance.

It may not:

- emit target artifacts directly;
- keep frontend-specific semantic objects in the contract;
- rely on process-global registration;
- preserve executable callbacks in transport;
- create operations, storage, or views implicitly without visible compiled facts;
- serialize its builder graph as an alternate IR.

The criterion for authoring quality is not minimal keystrokes. It is whether the compiled contract remains obvious, complete, and portable.

## Refine the kernel through evidence

Kernel growth should use a proposal containing:

1. real problem examples from at least two projects;
2. target-neutral definition;
3. rejected representations using existing concepts;
4. typed object/relation/facet/value decision;
5. identity and containment rules;
6. validation and diagnostics;
7. compatibility classification;
8. selector and context exposure;
9. serialization, ordering, and digest behavior;
10. pack simulations for different targets;
11. authoring simulations for different frontends;
12. migration and version impact;
13. explicit non-goals.

A proposal should be rejected when its strongest argument is convenience for one pack.

## Refine selectors conservatively

Selectors are a public query surface and therefore part of behavior compatibility. Prefer fixed, named, root-first selectors over an arbitrary graph language.

A new selector should:

- represent a recurring pack requirement;
- have deterministic scope and ordering;
- expose a known singular or collection context;
- be explainable in plan output;
- avoid requiring packs to reconstruct parent ownership;
- remain compatible across authoring frontends.

Complex filtering logic in manifests is a warning sign. It is usually better to add a well-defined semantic role or fixed selector than to expose unrestricted traversal.

## Refine packs through progressive disclosure

Simple packs should be mostly understandable from their filesystem:

```text
DryvPack.yaml
templates/
_partials/
fixtures/
README.md
```

The manifest should declare only behavior that cannot be inferred safely:

- pack identity and compatibility;
- options and bindings;
- include/exclude rules;
- dynamic selection folders;
- explicit generated dependencies and symbols;
- commands and approvals;
- project-owned overrides permitted by the pack.

Advanced dependency and export features should not burden a pack that emits independent files.

## Refine usage toward one obvious workflow

The common project lifecycle should be:

```text
1. Obtain or author a canonical contract.
2. Select pack sources and outputs.
3. Validate project, contract, packs, and plugins.
4. Resolve and lock dependencies.
5. Inspect the complete plan.
6. Generate transactionally.
7. Run generated-project verification.
8. Inspect trace and state when needed.
```

Configuration should answer these questions without runtime source reading:

- Which semantic input is used?
- Which packs are active and in what order?
- Where does each pack come from?
- What does each pack generate?
- Which options and bindings are applied?
- Where is output written?
- Which commands may run?
- What is locked?

## Refine product naming

A stable vocabulary should distinguish:

- **Codepot:** the wider ecosystem and product vision;
- **Dryv:** the canonical derivation runtime and package family;
- **authoring frontend:** a language-specific compiler into Dryv IR;
- **canonical Runtime IR:** the only portable semantic authority;
- **pack:** reusable emission behavior and templates;
- **template engine:** renderer of prepared contexts;
- **target adapter:** validator and target path/module fact provider;
- **usage configuration:** project-owned connection of inputs, packs, and outputs;
- **CLI/IDE/MCP/web client:** frontend over public runtime operations;
- **Codepot language:** a possible native authoring language, not the runtime semantics themselves.

Product names may evolve, but responsibility names should remain stable.

## Anti-goals

Codepot should explicitly reject these goals:

- model all possible software;
- generate arbitrary algorithms correctly from structure alone;
- remove the need for developers;
- make generated output the only acceptable code;
- embed one framework’s architecture in core;
- allow plugins to add arbitrary semantic roots;
- infer critical behavior from filenames or tags;
- automatically merge arbitrary manual edits;
- guarantee compatibility for unknown metadata;
- operate as a proprietary pack credential system;
- require a marketplace for normal use;
- optimize incremental generation before full correctness;
- measure success by generated line count.

## The refinement rule

Whenever a feature is proposed, ask:

> Does this make canonical meaning, deterministic derivation, safe ownership, or explanation stronger?

If the answer is no, the feature probably belongs outside the runtime or should not be built yet.
