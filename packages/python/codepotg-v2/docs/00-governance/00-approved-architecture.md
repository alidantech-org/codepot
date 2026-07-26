# Approved CodepotG v2 architecture

This document is the highest-priority design contract for the clean rewrite under `packages/python/codepotg-v2`.

An implementation that conflicts with this document is incorrect even when it resembles the existing generator. The detailed semantic contract is [`04-closed-semantic-kernel.md`](04-closed-semantic-kernel.md).

## Clean-room boundary

- The existing `packages/python/codepotg` package remains the complete implementation for old behavior.
- CodepotG v2 does not import old implementation modules.
- CodepotG v2 does not implement compatibility decoders for old `tasks` configuration or `paths.yaml`.
- Existing packs may be studied for real requirements, but are re-authored into the v2 contracts.

## Product boundary

CodepotG v2 is a deterministic semantic-to-artifact compiler and application-system macro engine.

It owns:

- a closed, typed, versioned semantic kernel;
- source normalization contracts;
- fixed root-first selectors;
- filesystem-driven pack discovery;
- artifact, symbol, dependency, path, and impact planning;
- validation, safety, locking, staging, and writing.

It does not secretly author application code. Templates, macros, partials, and static files own every emitted character.

## Closed semantic kernel

Every semantic object, relation, facet, selector, validation rule, and template-context property is known by CodepotG in advance.

- Source adapters translate into the known kernel.
- Packs and templates consume the known kernel.
- Plugins cannot add semantic node kinds, relations, facets, selector grammar, or template-context properties.
- Unknown source metadata may be preserved only through bounded immutable `extensions`, `raw`, and provenance values.
- Growth requires an intentional kernel change, tests, documentation, compatibility rules, and IR/behavior versioning.

The implementation may use typed graph indexes internally. Public IR and template contexts are explicit typed objects, not generic string-keyed node/edge/fact bags.

## Semantic topology

The primary root is:

```text
contract.groups
```

A group contains known collections:

```text
group.schemas
group.operations
group.views
group.storage.mappings
group.workflows
group.policies
group.events
group.groups
```

`group` replaces ambiguous neutral uses of `resource`, `service`, `module`, `feature`, and similar framework/domain terms. Templates may still emit those forms.

Paths and contexts always read outer-to-inner:

```text
group.operations
operation.inputs
operation.facets.http
workflow.steps
step.compensation.operation
```

Reversed roots such as `http.groups`, `events.operations`, and `storage.groups` are not part of the contract.

## Schema contract

`schema.kind` describes structure only:

```text
primitive, literal, enum, object, array, map, tuple,
union, intersection, alias, unknown
```

`model`, `entity`, `request`, `response`, `class`, `interface`, `type`, `struct`, and `record` are not schema kinds.

A source may assign a controlled role such as `dto`; a DTO remains a schema. Input/output direction belongs to operation schema-use relationships, because one schema may be reused in both directions.

Semantic fields expose facts and presence-aware constraints. Templates choose how those facts map to validators, types, modifiers, storage declarations, documentation, or framework syntax.

## Operation contract

The neutral operation contract is:

```text
operation
├── inputs
├── outputs
├── failures
├── effects
└── facets
```

Initially approved operation facets are:

```text
operation.facets.http
operation.facets.access
operation.facets.trigger
operation.facets.execution
operation.facets.events
```

Facets are kernel-defined typed perspectives, not third-party extension modules. Unknown facet names are errors.

A listener is normally an operation with a trigger facet. Supporting behavior around one operation is represented through execution phases that reference ordinary operations. Reusable access policies live under `group.policies`, while access facets expose declared and effective policy facts.

## Views, storage, events, and workflows

- `group.views` represents renderable/navigable interaction units without assuming web, mobile, desktop, terminal, page, screen, component, or widget output.
- `group.storage.mappings` connects schemas to stores, fields, keys, indexes, relations, and constraints. `entity` is generated vocabulary, not a neutral kernel object.
- `group.events` declares occurrences. `operation.effects.events` records caused occurrences; event trigger/delivery facts live in known operation facets.
- `group.workflows` describes orchestration through steps, transitions, waits, decisions, parallel branches, failures, effects, and known facets.
- A workflow step has one forward operation and may optionally reference one compensation operation. Compensation is corrective work, not an assumed exact inverse.

## Two authored YAML files

1. `codepotg.yaml` contains project-owned configuration.
2. `CodepotgPack.yaml` contains pack-owned configuration.

No registry alias file or extra user-edited pack configuration is required.

## Project ownership

`codepotg.yaml` owns:

- project identity;
- named semantic inputs;
- executable names or paths;
- command policy and project before/after commands;
- ordered pack instances;
- each pack instance's direct source, input, output root, options, bindings, and project-owned overrides.

A pack instance declares its source directly:

```yaml
source:
  local: ./packs/typescript-sdk
```

or:

```yaml
source:
  git: https://github.com/alidantech-org/codepotg-packs.git
  ref: typescript-sdk/v2.4.1
  path: packs/typescript-sdk
```

`source` locates the pack. `input` names the semantic project source consumed by the pack.

## Pack ownership

`CodepotgPack.yaml` owns only information that cannot be inferred safely from the pack filesystem:

- pack identity, compatibility, description, options, and public bindings;
- include/exclude rules;
- registered emission selections;
- pack-relative emission paths;
- fixed selectors;
- explicit generated dependency declarations;
- exported emission groups and declared symbols;
- executable defaults and exact before/after command arguments.

The manifest does not register every template or static file.

## Filesystem-driven templates

The default content root is `templates/`.

- Literal template paths are rendered at the same relative output path.
- The recognized template-engine suffix is removed.
- Literal static and binary files are copied unchanged.
- `_partials/` is available to templates and is not emitted.
- A pack-root `.gitignore` and manifest `include`/`exclude` rules control discovery.
- A literal `.gitignore` control file is not emitted. A pack that generates one authors `.gitignore.jinja`.
- Only folders whose whole segment is `{selectionKey}` require a manifest entry.

## Root-first fixed selectors

CodepotG exposes a documented, versioned selector registry rather than arbitrary graph queries or pack-authored traversal.

Preferred examples:

```text
groups.each
groups.schemas.each
groups.schemas.objects.each
groups.schemas.enums.each
groups.schemas.dtos.each
groups.operations.each
groups.operations.inputs.each
groups.operations.outputs.each
groups.operations.failures.each
groups.views.each
groups.storage.mappings.each
groups.workflows.each
groups.policies.each
groups.events.each
```

Inside an active group context, selectors start with the parent:

```text
group.operations.each
group.storage.mappings.each
group.workflows.each
```

Global selectors such as `operations.each` may exist for genuine project-wide reports or indexes but are discouraged for ordinary generation. Packs should not select globally and reconstruct group ownership manually.

`.each` repeats and exposes the known singular item. `.all` emits once with the known collection. Optional inline aliases may not shadow active contexts.

## Path expressions and naming

Path and filename expressions use:

```text
{selectionKey}   registered selection folder
{root}           no-path built-in selection folder
(expression)     bounded typed expression
((literal))      literal parentheses
```

Square brackets remain literal for framework routes.

Every named semantic value follows one ordering:

```text
x.name.{casing}.{number}
```

Examples:

```text
field.name.camel.original
schema.name.pascal.singular
operation.name.kebab.plural
```

Short number aliases `o`, `s`, and `p` are allowed. Reversed forms such as `name.singular.camel` are not.

Semantic records do not expose invented `fileName`, `filePath`, or `directory` properties.

## Imports, exports, and symbols

Cross-selection dependencies are mandatory and explicit:

```yaml
imports:
  schemaTypes: schemaTypes
```

The mapping is `localName: selectionKey`.

The planner resolves provider artifacts, semantic matches, declared symbols, scope, destinations, and module/path facts before rendering. It rejects missing providers, ambiguity, conflicts, cycles, and undeclared dependencies.

Templates author all import and export syntax. Language adapters may validate target names and calculate target-aware module/path facts, but they do not emit import/export statements, types, literals, comments, decorators, validators, or framework code.

Barrels are ordinary authored templates whose selections declare ordered `exports`. Generated symbols are declared explicitly; CodepotG does not parse rendered source to guess them.

## Adapter boundary

- Source adapters load supported formats and normalize only into the closed semantic kernel.
- Core owns semantic validation, selector resolution, filesystem discovery, expressions, dependency/impact graphs, artifact planning, safety, and locking.
- Language adapters detect supported target suffixes, validate target identifiers/filenames, calculate target-aware module/path facts, and expose typed target capabilities. They do not author code syntax.
- Template-engine adapters render already planned immutable contexts and do not choose destinations.
- Pack providers resolve local and generic Git sources using controlled snapshots.
- Ecosystem adapters plan known project/toolchain intent but do not expand the semantic kernel.

## Complete planning before rendering

CodepotG plans every invocation, destination, semantic identity, symbol, generated dependency, export, binding, command, approval, collision, and ownership action before rendering.

Planning supports:

```text
semantic change
→ affected relations
→ affected selections
→ affected invocations
→ affected artifacts
```

Dry-run and blast-radius inspection are first-class plan outputs. Deterministic full generation comes first; incremental generation may be added only with conservative dependency tracking and safe fallback to broader regeneration.

The dependency lock records source, pack, plugin, and behavior identity. Generated output hashes belong to ownership/generation state, not the dependency lock.

Invalid plans never call renderers or writers.

## Commands and executables

Commands contain exact opaque arguments authored by the project or pack. CodepotG does not transform dependency maps into package-manager commands and does not understand npm, pnpm, Dart, Flutter, or other install syntax in core.

A pack may provide executable defaults. The project may provide or replace executable names/paths. Host security policy remains authoritative, and downloaded pack commands require approval by default.

## Git sources and locking

There is no separate `registries` plus `use` indirection. Every pack instance carries one direct local or Git source. Branches and tags resolve to immutable commits in `codepotg.lock.yaml`. The lock records requested source, resolved commit, pack identity/version, subdirectory, content digest, plugin/behavior versions, and no credentials.

## Agent rule

Every agent must read this document, `04-closed-semantic-kernel.md`, the relevant detailed design, the matching task ledger, and `tasks/PARALLEL_WORK.md` before implementation. Design changes require explicit approval and matching documentation/task updates before code is written.
