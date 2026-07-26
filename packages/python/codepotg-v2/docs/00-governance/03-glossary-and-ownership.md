# Glossary and ownership matrix

This glossary prevents agents from reusing old or framework-specific terms with incorrect CodepotG v2 meanings. The closed semantic contract is defined in [`04-closed-semantic-kernel.md`](04-closed-semantic-kernel.md).

## Project and pack terms

### Project

The user's repository or configured generation workspace described by `codepotg.yaml`. A project may contain several pack instances, output roots, toolchains, and target syntaxes.

A project is not a language and is not a template pack.

### Semantic source

A named input normalized by a source adapter into the closed neutral kernel. A source is not a pack and does not choose output architecture.

### Template pack

A reusable generation product described by `CodepotgPack.yaml` and its filesystem content. It declares selections, output paths, generated dependencies, symbols, options, bindings, commands, and documentation.

### Pack instance

One project-owned configuration of a pack under `codepotg.yaml`. The same pack may have several instances using different sources, outputs, options, bindings, and commands.

### Pack file descriptor

The typed description created for one discovered pack source file after ignore rules and target/engine detection are applied.

### Template

A pack-authored file rendered through a template-engine adapter. Templates, macros, partials, and static files own every emitted character.

### Partial

A non-emitting template fragment included through the pack template registry. It must be target-compatible or target-neutral.

### Static file

A non-template text file copied without rendering.

### Binary file

A non-template binary asset copied byte-for-byte through the same plan/writer safety model.

### Barrel

An authored template receiving planned export descriptors. Core does not invent barrel text.

## Semantic-kernel terms

### Contract

One immutable normalized semantic document produced by a source adapter. Its primary root is `contract.groups`.

### Group

The neutral outer scope containing schemas, operations, views, storage mappings, workflows, policies, events, child groups, documentation, and known facets.

A group is not inherently a REST resource, service, module, feature, namespace, package, or bounded context. Templates may generate those forms.

### Schema

A structural data definition. `schema.kind` is one of the kernel-defined structural kinds such as primitive, enum, object, array, map, union, or alias.

`model`, `entity`, `request`, `response`, class, interface, type, struct, and record are not schema kinds.

### Schema use

A relation from an operation input/output or another known semantic location to a schema. Direction and use-specific facts belong to the relation, not permanently to the schema.

### DTO role

A controlled optional role assigned to a schema when the source explicitly identifies transport-shaped data. A DTO remains a schema and is not a separate hierarchy.

### Operation

Executable behavior described by inputs, outputs, failures, effects, and known facets.

### Input

A schema-use record describing data required by an operation.

### Output

A schema-use record describing a successful direct result of an operation.

### Failure

A declared operation or workflow failure possibility. It is not limited to HTTP status codes or exceptions.

### Effect

A consequence beyond a direct returned result, such as causing a declared event occurrence.

### Facet

A kernel-defined typed perspective attached only at documented semantic locations. Initial operation facets include HTTP, access, trigger, execution, and events.

A facet is not an extension plugin. Packs and adapters cannot register new facets.

### Listener

An operation whose execution is initiated through a known trigger facet, such as an event or schedule trigger. Listener is a usage description, not a separate executable hierarchy.

### Policy

A reusable access declaration under `group.policies`. Policy application and effective inherited access facts are exposed through known access facets.

### Hook

A typed execution-phase relationship from one operation to another operation. Hooks may run before, around, after success, after failure, or after completion. Hook is not an open-ended executable node kind.

### View

A renderable or navigable interaction unit under `group.views`. It may contain parts, triggers, flows, and access facts without assuming web, mobile, desktop, page, screen, component, or widget output.

### Storage mapping

A relation under `group.storage.mappings` connecting a schema to store, field, key, index, relation, and constraint facts.

`entity` is generated ORM vocabulary, not a neutral kernel object.

### Event

A declared occurrence under `group.events`. Caused occurrences appear in operation/workflow effects; event start and delivery facts appear in known trigger/event facets.

### Workflow

A first-class orchestration object under `group.workflows` with inputs, outputs, steps, transitions, failures, effects, and known facets.

### Workflow step

A typed orchestration step. An operation step references one forward operation and may optionally reference one compensation operation. Other known structures may include decision, parallel, wait, and end.

### Compensation

Corrective behavior invoked for a successfully completed workflow step when later workflow execution fails or another declared condition applies. Compensation is not assumed to be a perfect rollback or inverse.

## Generation terms

### Target syntax

The language or textual syntax produced by a template, such as TypeScript, Dart, YAML, Markdown, SQL, JSON, or Dockerfile syntax.

### Language adapter

An installable package that identifies target suffixes, validates target identifiers/filenames, calculates target-aware module/path facts, and publishes typed target capabilities.

It does not emit types, literals, imports, exports, comments, decorators, validators, or framework code.

### Template-engine adapter

An installable package that safely compiles and renders templates from immutable prepared contexts. It does not own target syntax, destinations, or semantic meaning.

### Source adapter

An installable package that loads one source format and normalizes it into the known CodepotG kernel. It cannot extend the kernel.

### Ecosystem adapter

A package that understands known project manifests, package managers, toolchains, and setup actions. It does not add semantic concepts or render application code.

### Pack provider

A service that resolves local or Git pack locations into immutable local snapshots. It does not interpret semantic sources or templates.

### Selection

A pack-owned declaration using one fixed, versioned, root-first selector to establish invocation cardinality and immutable template context.

### Template invocation

One planned rendering of one template descriptor with one selected context/aggregate, one target descriptor, one engine, effective options/bindings, generated dependencies, and a fixed destination.

### Binding

A pack-declared public integration point supplied by the project, such as a module, project path, package, value, text, or artifact reference.

### Generated dependency

An explicit selection-to-selection dependency declared under `imports` or `exports`. The planner resolves provider artifacts, semantic identity, symbols, scope, and path/module facts. Templates author the syntax.

### Symbol

A pack-authored declaration of a name an artifact provides. CodepotG does not parse rendered source to discover symbols.

### Generation plan

The complete immutable validated description of normalized semantics, sources, packs, files, selections, invocations, destinations, symbols, dependencies, bindings, commands, approvals, impact, and readiness before rendering.

### Artifact

One planned generated or copied output with stable identity, destination, selected semantic identity, source template/static descriptor, declared symbols, dependencies, lifecycle, and ownership.

### Impact graph

The planned relation from semantic changes to affected relations, selections, invocations, and artifacts. It powers dry-run and blast-radius inspection and may later support conservative incremental generation.

### Ownership/generation-state manifest

Writer metadata recording generated artifact ownership, content digests, and prior generation state for safe updates, cleanup, drift reporting, and caching.

### Lock file

`codepotg.lock.yaml`, which records immutable pack/source/plugin/behavior identity for reproducibility. Generated output hashes do not belong in the dependency lock.

## Naming contract

Named semantic values always use:

```text
x.name.{casing}.{number}
```

For example:

```text
field.name.camel.original
schema.name.pascal.singular
operation.name.kebab.plural
```

Short number aliases `o`, `s`, and `p` are allowed. Do not reverse casing and number order.

## Ownership matrix

| Concern | Project | Pack/template | Core/planner | Adapter/plugin | Host |
|---|---:|---:|---:|---:|---:|
| Semantic source location/options | owns | may require named input | resolves | source adapter loads/normalizes | restricts access |
| Semantic kernel | no | consumes | owns and versions | cannot extend | no |
| Pack source | owns instance locator | identifies itself | resolves | provider fetches | restricts network/Git |
| Output root | owns instance root | declares relative paths | validates/plans | writer commits | restricts filesystem |
| Selection | no internal details | owns fixed selector choice | compiles registry | cannot add grammar | no |
| Generated text | no | owns every character | supplies facts/plans | engine renders; language validates paths | no |
| Generated dependency | supplies external bindings | declares imports/exports/symbols | resolves semantic/provider graph | language may calculate path facts | no |
| Target syntax | no global choice | target inferred from authored file | resolves descriptor | validates target/path capabilities | may restrict plugins |
| Commands | owns policy and project commands | owns exact pack commands | plans/validates | executor resolves | final authority |
| Static/binary content | configures output only | owns bytes/layout | discovers/plans | writer copies | filesystem policy |
| Lock | requests frozen/update behavior | contributes identity | owns format and validation | providers/plugins supply versions | protects credentials |

## Forbidden terminology and shortcuts

Agents must not say or implement:

- `resource`, `model`, or `entity` as neutral v2 kernel objects;
- `frontend` or `ui` as top-level semantic roots;
- class/interface/type/struct/record as schema kinds;
- `http.groups`, `events.operations`, `access.operations`, or other reversed roots;
- arbitrary pack-authored selector queries, traversal, `where`, or depth expressions;
- third-party facet modules or adapter-defined semantic properties;
- language adapters that generate imports, exports, types, literals, comments, validators, decorators, or framework syntax;
- templates that write files or run commands;
- root barrels generated automatically by core;
- semantic `fileName`, `filePath`, or `directory` conveniences;
- output hashes stored in the dependency lock;
- migration as runtime support for old configuration.
