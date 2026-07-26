# Planning, impact analysis, execution, and transactional output

## Complete plan before rendering

CodepotG compiles a complete immutable generation plan before any template renders or destination file changes.

The pipeline is:

```text
load and normalize sources
→ validate closed semantic kernel
→ discover packs/files
→ run root-first fixed selections
→ register artifact identities/destinations/symbols
→ resolve generated dependencies and path/module facts
→ validate complete plan and impact graph
→ render into staging/memory
→ validate staged artifacts
→ commit through a writer
```

The plan contains:

- resolved project and pack configuration;
- plugin, IR, naming, selection, and behavior versions;
- source digests and normalized semantic identity;
- immutable groups, schemas, operations, views, storage mappings, policies, events, and workflows;
- file descriptors and include/partial dependencies;
- root-first selector instances and active parent scopes;
- template invocations;
- resolved project bindings;
- generated dependency providers and requirements;
- declared symbols and exports;
- provider destinations and target-aware module/path facts;
- output paths and lifecycle modes;
- commands, capabilities, approvals, readiness, and manual actions;
- semantic-to-artifact impact relations.

## Closed semantic validation

Before artifact planning, CodepotG validates kernel semantics including:

- missing schema references;
- invalid operation input/output/failure uses;
- unknown groups or invalid ownership;
- invalid storage fields, keys, indexes, relations, or constraints;
- missing policy references or invalid access inheritance;
- invalid execution-hook operation references/order/mappings;
- missing event declarations or invalid event trigger/delivery references;
- invalid workflow steps, transitions, branches, waits, and compensation mappings;
- unknown facets or unsupported attachment locations.

Source adapters may diagnose source-format problems, but core owns the meaning and validation of the normalized kernel. Adapters and packs cannot add semantic validators for invented concepts.

## Graphs and indexes

The planner may use typed graph/index structures internally for:

- semantic references;
- group containment;
- workflow step/transition/compensation relationships;
- event causes, producers, consumers, and listeners;
- view-trigger-to-operation relationships;
- storage-schema relations;
- access policy uses and inheritance;
- execution hooks;
- template includes;
- selection/provider/artifact dependencies;
- generated imports/exports;
- command/action phase ordering;
- blast-radius and incremental impact.

These graphs are internal implementation structures. Templates receive typed contexts such as `operation.inputs`, `step.compensation.operation`, and `mapping.schema`, not generic node/edge query APIs.

Cycles, missing providers, ambiguous providers, output collisions, incompatible targets, forbidden capabilities, and invalid semantic relationships are diagnosed before rendering.

## Artifact identity

Each planned artifact has a stable logical identity derived from known inputs such as:

```text
pack instance identity
+ selection key
+ selected semantic identity/scope
+ template relative path
+ target descriptor
```

Destination path is not the artifact's sole identity.

A semantic identity remains stable across renames only when the source supplies or CodepotG can derive a stable identity independently of the display name. CodepotG must not guess that delete-plus-add is a rename.

## Template invocation

The central execution unit is `TemplateInvocation`, not a language-wide generation pipeline.

Each invocation contains:

- one file descriptor;
- one target descriptor/validator;
- one template engine;
- one fixed selection instance or aggregate;
- active outer-to-inner semantic contexts;
- resolved options and external bindings;
- generated dependency descriptors under declared local names;
- export descriptors;
- declared symbols;
- fixed destination and dependency order;
- immutable render context.

Outputs are fixed before rendering.

## Generated dependency planning

A selection's `imports` and `exports` declare artifact dependencies by selection key.

The planner:

- matches providers by semantic identity and active scope;
- uses explicit symbols rather than parsing rendered source;
- computes required provider artifacts and symbols;
- resolves relative destination/path facts;
- requests target-aware module-path validation/normalization where needed;
- rejects ambiguity, missing providers, conflicts, and cycles;
- exposes immutable descriptors to templates.

Templates author every import/export statement. Language adapters do not inject syntax.

## Rendering

Rendering produces staged artifact content. Templates never receive destination filesystem handles.

Templates, macros, partials, and static files own every emitted character. CodepotG provides facts, relationships, names, symbols, paths, and ordering; it does not render types, literals, validators, decorators, comments, framework logic, workflow logic, or import/export statements on behalf of packs.

Static and binary descriptors produce staged copy artifacts through the same plan and lifecycle validation.

## Explain and provenance

Every planned artifact must be explainable through:

```text
source semantic identity and provenance
→ fixed selector and active scope
→ template/static descriptor
→ options/bindings/generated dependencies
→ declared symbols
→ destination
```

Initial explain support is artifact- and symbol-level. Exact generated-line source maps are optional engine-specific future work and must not be promised as a core guarantee until instrumented rendering exists.

## Impact and blast radius

The plan records:

```text
semantic item/relation
→ selections that depend on it
→ invocations created from those selections
→ provider/consumer artifacts
→ exported/barrel artifacts
```

A dry-run or inspection client can answer:

- which semantic change caused an artifact to be affected;
- which generated artifacts consume one schema, operation, policy, event, workflow, or storage mapping;
- which clients/views/workflows are downstream of a changed operation;
- why an artifact will be created, changed, deleted, or left unchanged.

The blast-radius browser is built on the same plan and generation-state data; it is not a separate source of truth.

## Incremental generation

Deterministic complete generation is implemented and proven first.

Later incremental generation may use:

- semantic digests and relation changes;
- fixed selection scope;
- template and partial digests;
- option/binding changes;
- generated dependency edges;
- provider/export graphs;
- target/engine behavior versions;
- conservative template-context dependency sets;
- optional safe read tracing from immutable context proxies.

If exact impact cannot be proven, CodepotG regenerates a broader safe scope. Incremental execution must never sacrifice deterministic equivalence with a complete generation.

## Writers

Artifact writers are ports:

- transactional filesystem writer;
- memory writer;
- archive writer;
- controlled external writers added later.

The filesystem writer stages the whole generation in a private area, validates it, then commits as one transaction as far as the platform safely permits.

## Path safety

Before staging:

- normalize separators;
- reject absolute paths unless an explicit writer contract owns them;
- reject traversal;
- enforce output roots;
- reject invalid/reserved segments;
- validate case-folded collisions where relevant;
- reject symlink escapes;
- validate managed/protected ownership.

## Exact comparison

Changed-content detection uses exact bytes or canonical line-ending policy declared by the writer. It must not ignore layout, comments, whitespace, or syntax-significant formatting.

## Ownership and generation state

Committed output records:

- pack and instance identity;
- artifact identity;
- selected semantic identity/scope;
- source file descriptor;
- content digest;
- declared symbols and dependency identities;
- lifecycle mode;
- generation session/lock identity;
- timestamp where needed outside deterministic content.

This ownership/generation-state manifest supports safe cleanup, drift reporting, impact inspection, cache reuse, and later incremental generation.

Generated output hashes do not belong in `codepotg.lock.yaml`. The lock records resolved inputs and behavior identity; the ownership/generation-state manifest records outputs.

## Lifecycle

Supported writer intent includes:

- managed: CodepotG may replace or remove owned output;
- immutable: existing differing content is an error;
- protected: never overwrite without explicit project action;
- unmanaged: emit only when absent or according to explicit policy.

Project and host policies may tighten pack lifecycle requests.

## Writer rollback

Writer rollback is distinct from workflow compensation.

Failures before commit leave destination state unchanged. Commit uses backup/replace operations and restores previous content on partial failure where supported.

The result must accurately report platform limitations or incomplete rollback; it must not claim atomicity that did not occur.

## Dry run and inspect

Dry run compiles the semantic and artifact plan and, when requested, renders to memory without committing. It reports:

- files to create/change/delete/leave;
- semantic causes and affected dependents;
- generated dependency and export changes;
- commands and approvals;
- unresolved bindings and manual actions;
- exact plugin, pack, source, IR, naming, and selection versions.

## Cache

Content-addressed keys include all behavior-affecting inputs:

- source and normalized semantic digest;
- IR/naming/selection behavior versions;
- source adapter version;
- target descriptor/path-validation behavior;
- template engine version/rules;
- pack commit and manifest/content digest;
- template/include digests;
- options/bindings;
- selection identity and active scope;
- generated dependency/provider identities;
- output-planning behavior version.

Cache collisions caused by omitted behavior inputs are correctness defects.

## Readiness

Flexible fragment generation can complete with explicit actions. Strict mode applies project/host readiness policy after planning and before commit.

Possible result states include:

```text
ready
generated_with_warnings
generated_with_actions
partially_generated
failed
cancelled
```

## Required tests

- every closed-kernel reference and relationship diagnostic;
- unknown facet/selector/context rejection;
- deterministic plan ordering;
- no rendering before semantic and plan validity;
- stable artifact identity separate from destination;
- root-first scope preservation;
- generated provider/symbol/path resolution;
- template ownership of emitted syntax;
- static/template parity through planning;
- output collision and path safety;
- exact byte comparison;
- ownership and cleanup;
- writer transaction rollback;
- workflow compensation remaining a semantic concern, not writer behavior;
- cancellation before commit;
- dry-run immutability;
- artifact/symbol explain traces;
- semantic-to-artifact blast-radius reporting;
- complete versus incremental equivalence when incremental generation is added;
- cache invalidation for every behavior input;
- honest readiness status.
