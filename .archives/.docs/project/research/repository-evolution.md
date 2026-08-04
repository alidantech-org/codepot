# Codepot repository evolution and architectural lessons

## Purpose

This document reconstructs how Codepot moved from an OpenAPI-centered contract and generator workflow toward the current Dryv three-tier architecture. It records the value of earlier implementations without allowing superseded vocabulary or coupling to become the current contract.

The history matters because Codepot was not conceived fully formed. Its strongest current rules are responses to practical friction found in earlier versions.

## Timeline at a glance

```text
Typed OpenAPI authoring
    codepot-openapi
        ↓
OpenAPI-normalizing Jinja generation
    codepotg
        ↓
Frontend-neutral JavaScript runtime rewrite
    codepotx
        ↓
Generalized CodepotG v2 package family
        ↓ rename and boundary hardening
    Dryv runtime + authoring + CLI + plugins
        ↓
Future native Codepot language and wider platform
```

## Era 1 — typed API contract authoring

### Product shape

The original [`codepot-openapi`](../packages/nodejs/codepot-openapi/README.md) package let TypeScript developers define typed API contracts and compile them to OpenAPI 3.1 JSON or YAML. It used OpenAPI as a portable and ecosystem-compatible transport while preserving richer generator information in `x-codegen` metadata.

Useful ideas proven in this era included:

- typed reusable properties;
- structural schemas and references;
- deterministic compilation;
- schema projections;
- versioned resources and operations;
- validation before output;
- a contract that could be consumed outside the authoring process.

### Pressure that caused growth

Real application generation needed more than HTTP paths and schemas. Codepot began carrying:

- entity and relation intent;
- access rules;
- hooks and effects;
- frontend and UI guidance;
- implementation information;
- generator-specific placement and grouping.

OpenAPI extensions made this possible, but the semantics were no longer naturally governed by OpenAPI. The project was using an API description as a carrier for a broader application model.

### Lesson retained

A portable contract is extremely valuable, but the transport format must not become the semantic authority merely because it is familiar.

## Era 2 — CodepotG as the practical generation engine

### Product shape

The archived [`codepotg`](../archives/codepotg/README.md) runtime consumed OpenAPI documents, inferred a normalized generation model, and rendered Jinja template packs. It accumulated substantial practical functionality:

- JSON and YAML input;
- streamed/indexed JSONL infrastructure;
- normalized resource, operation, schema, entity, access, frontend, and documentation views;
- bundled TypeScript, Next.js, Dart, and debug packs;
- project-owned packs;
- `paths.yaml` planning;
- graph selections and dependencies;
- explicit providers and barrels;
- bounded template contexts;
- managed and immutable output modes;
- protected and clean roots;
- dry runs and structured diagnostics;
- guarded cleanup and atomic writes;
- before/after commands;
- memory tracing and performance work.

This implementation is important evidence. It shows that the project’s safety and pack ideas came from real generator behavior rather than only architecture discussion.

### Pressure that caused growth

The implementation exposed several structural problems:

1. **Input-model mismatch.** OpenAPI remained the input even when generators needed non-HTTP application meaning.
2. **Inference as hidden semantics.** The generator normalized and inferred concepts that were not always explicitly authored.
3. **Vocabulary coupling.** Terms such as resource, entity, frontend, and UI risked becoming universal runtime concepts.
4. **Configuration accumulation.** Tasks, paths, selections, compatibility behavior, and lifecycle controls grew around the historical format.
5. **Runtime/frontend mixing.** A mature generator needed reusable operations for CLI, tests, servers, editors, and agents.
6. **Backward-compatibility pressure.** Supporting old and new pack forms simultaneously complicated reasoning.

### Lessons retained

- output ownership and cleanup require first-class state;
- generation must be planned before mutation;
- templates need bounded and documented contexts;
- generated dependencies must be explicit;
- large inputs need infrastructure representations without creating a second semantic model;
- a dry run must represent the actual plan, not a rough preview;
- generator safety is a product capability, not an optional CLI flag.

## Era 3 — CodepotX and stable runtime artifacts

### Product shape

[`codepotx`](../packages/nodejs/codepotx/README.md) was a JavaScript rewrite that separated:

```text
contract
authoring
templating
generation
platform
runtime
```

It introduced or reinforced:

- JSON-safe artifacts between major layers;
- runtime requests and lifecycle events;
- memory and filesystem platform adapters;
- explicit package exports;
- deterministic planning and manifests;
- an external CLI consuming the public runtime;
- architecture tests for dependency direction.

### Pressure that caused further refinement

CodepotX still inherited substantial authoring and compatibility vocabulary from the OpenAPI era. The project also needed a more explicit answer to these questions:

- What is the only semantic authority?
- Can plugins add semantics?
- What belongs to a language adapter?
- Who owns IR serialization?
- Who owns emitted syntax?
- How can several authoring languages remain equivalent?
- Which selectors are safe and portable?
- How should pack dependencies be resolved before rendering?

### Lessons retained

- the runtime must be independent of its CLI;
- public artifacts must be immutable, deterministic, and serializable;
- filesystem, Git, process, and cache behavior belong behind ports/adapters;
- package boundaries require executable architecture tests;
- machine output and human presentation are separate contracts.

## Era 4 — generalized CodepotG v2 and Dryv

### Product shape

The latest package family under `packages/python/*` defines Dryv as the software-derivation runtime:

```text
dryv
dryv-author
dryv-cli
dryv-template-jinja
dryv-language-typescript
dryv-language-dart
```

The approved architecture establishes:

- one closed, typed, versioned semantic kernel;
- several authoring frontends compiling to one immutable contract;
- runtime-owned validation, canonical transport, selectors, planning, impact, writing, and state;
- pack-owned templates, static files, paths, selections, symbols, dependencies, options, and bindings;
- language adapters limited to target validation and path/module facts;
- template engines limited to rendering prepared immutable contexts;
- direct local or Git pack sources with immutable locking;
- full planning before rendering;
- conservative incremental generation only after correct full generation;
- no compatibility runtime for archived generator contracts.

The name Dryv usefully distinguishes the reusable derivation runtime from the wider Codepot ecosystem and future native language.

## Evidence status

The active progress log records three different levels of maturity:

### Demonstrated baseline

On 2026-07-27, the pre-rebrand CodepotG v2 package baseline recorded:

- 461 passing tests and one skipped test;
- core, authoring, Jinja, TypeScript, and Dart package coverage;
- lint and formatting success;
- generated TypeScript compilation and Dart analysis.

### Implementation checkpoints

On 2026-07-28, the package family was renamed to Dryv, stale expectations were removed, a runtime facade was exposed, and the CLI was extracted. The progress document records these as implemented checkpoints but explicitly requires post-rebrand verification.

### Architectural commitments

The closed kernel, complete plan, plugin boundaries, pack contracts, lock behavior, impact model, and broader authoring scope are approved design commitments. Some are implemented, some partially implemented, and some planned.

A contributor must never treat those three categories as interchangeable.

## Renames and what they reveal

The sequence `codepot-openapi → codepotg → codepotx → CodepotG v2 → Dryv` can look unstable from outside. Internally it reveals an expanding understanding of the problem:

- **OpenAPI** proved portable typed contracts.
- **CodepotG** proved flexible pack-based generation and lifecycle safety.
- **CodepotX** proved the need for stable artifacts and a frontend-neutral runtime.
- **Dryv** establishes canonical semantic ownership and a clean three-tier architecture.

The danger is not the renames themselves. The danger is documentation and implementation drift between eras. The root README and public documentation must clearly identify:

- the current architecture;
- supported historical packages;
- archived packages;
- migration and compatibility policy;
- product naming and command ownership;
- which documents are normative.

## Ideas that should remain historical

The following historical patterns should not return as hidden current contracts:

- OpenAPI as the universal semantic root;
- `resource`, `entity`, `model`, `frontend`, or `ui` as universal kernel objects;
- pack-authored arbitrary graph traversal;
- runtime-generated import/export syntax;
- process-global plugin or authoring registries;
- templates receiving mutable builders or complete unbounded source documents;
- output paths inferred through undocumented naming conventions;
- rendering before the complete plan is valid;
- automatic overwrite or deletion based only on destination paths;
- CLI presentation behavior inside the runtime;
- compatibility shims that silently preserve obsolete semantics indefinitely.

## Ideas that should survive every implementation language

The following lessons are architecture-level and should remain regardless of whether the runtime is written in Python, TypeScript, Rust, Codepot language, or another language:

1. One canonical semantic authority.
2. Authoring compiles into that authority and stops there.
3. Transport serialization is runtime-owned.
4. Packs own emitted implementation text.
5. Selection and dependencies are explicit and inspectable.
6. Planning completes before rendering or writing.
7. Generated ownership is recorded and protected.
8. Runtime operations are reusable by every frontend.
9. Plugins have bounded authority and cannot redefine semantics.
10. Compatibility and traceability are first-class contracts.
11. Full deterministic generation is the correctness reference.
12. Historical implementations are evidence and test fixtures, not automatic compatibility obligations.

## Repository governance recommendation

The repository should maintain one concise active-state document at the root containing:

- current product names and roles;
- normative architecture links;
- package maturity labels;
- supported versus archived packages;
- exact verification status on the branch head;
- a dated migration/evolution table.

Archive content should remain searchable because it contains valuable design evidence. Every archived folder should begin with a notice that links to the active replacement and identifies which concepts are superseded.

## Final lesson from the evolution

The project did not grow because code templates were difficult. It grew because reliable generation requires explicit answers about meaning, ownership, dependency, compatibility, and change.

The current architecture is strongest when it treats those answers as stable contracts. It will regress if convenience reintroduces inference and hidden conventions faster than the runtime can explain them.
