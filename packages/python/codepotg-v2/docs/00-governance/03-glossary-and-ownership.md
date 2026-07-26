# Glossary and ownership matrix

This glossary prevents agents from reusing old terms with incorrect v2 meanings.

## Core terms

### Project

The user's repository or configured generation workspace described by `codepotg.yaml`. A project can contain several ecosystems, units, output roots, and target syntaxes.

A project is not a language and is not a template pack.

### Project unit

A scoped part of a repository with its own path and toolchain context, such as `backend`, `web`, or `packages/api_sdk`.

### Semantic source

A named input normalized by a source adapter into neutral IR, such as an OpenAPI file. A source is not a pack and does not choose output architecture.

### Template pack

A reusable generation product described by `CodepotgPack.yaml` and its content roots. It declares files, selections, outputs, bindings, rules, dependencies, setup, commands, and documentation.

A pack may be full-project, standalone-folder, extension, fragment, or a combination of traits.

### Pack instance

One project-owned configuration of a pack under `codepotg.yaml` `packs.<instance>`. The same pack may have several instances using different sources, outputs, options, bindings, and commands.

### Pack profile

A pack-defined named set of files/defaults such as `modular`, `monolithic`, or `minimal`. A profile never means language selection.

### Pack file descriptor

The single typed description created for one discovered pack source file after ignore rules, pattern defaults, and exact file configuration are applied.

### Template

A pack file rendered through a template-engine adapter. Its target syntax is inferred from its filename or explicitly declared only when ambiguous.

### Barrel

An authored template with `role: barrel` that receives planned export descriptors. It is not a special system-generated file category outside the unified file model.

### Partial

A non-emitting template fragment included through the pack template registry. It must be target-compatible or target-neutral.

### Static file

A non-template text file copied without rendering. It is emitted by default unless ignored or classified as non-emitting documentation.

### Binary file

A non-template binary asset copied byte-for-byte through the same plan/writer safety model.

### Target syntax

The language or textual syntax produced by a template, such as TypeScript, Dart, YAML, Markdown, SQL, JSON, or Dockerfile syntax. User-facing configuration groups this under `languages`; internal descriptors may classify programming, markup, data, configuration, query, or plain-text syntax.

### Template engine

The syntax used to render a template source, such as Jinja. It is inferred from the final filename suffix.

### Language adapter

An installable Python plugin that implements target-syntax identifiers, names, types, literals, comments, imports, exports, paths, capabilities, and typed language rules. It does not select templates or frameworks.

### Template-engine adapter

An installable Python plugin that safely compiles and renders templates from immutable prepared contexts. It does not own target syntax or output planning.

### Source adapter

An installable Python plugin that loads one source format and normalizes it directly into neutral IR.

### Ecosystem adapter

A plugin that understands project manifests, dependencies, package managers, toolchain capabilities, and typed setup actions for an ecosystem such as Node or Dart.

### Pack provider

A plugin/service that resolves local, Git, GitHub, or installed-distribution pack locations into immutable local snapshots. It does not interpret the pack manifest.

### Selection

A typed pack-owned declaration selecting, filtering, ordering, grouping, or aggregating neutral IR or planned artifacts for a file invocation.

### Template invocation

One planned execution of one template descriptor with one selected context/aggregate, one target adapter, one engine adapter, effective rules, resolved bindings, dependencies, and declared outputs.

### Binding

A pack-declared public integration point satisfied by a project pack instance. Examples include imports, project paths, package paths, barrels, values, text, package names, and artifact references.

### Rule

A typed adapter-owned configurable convention with a field descriptor, default, merge policy, override permission, security classification, documentation, and provenance.

### Override

A typed patch applied at a permitted project or template scope. It is not a recursive dictionary merge.

### Capability

A precise feature or artifact fact declared/provided/required by an adapter, template, pack, ecosystem, or generated artifact.

### Contribution

A typed desired change to a user-owned manifest or project, such as adding a dependency, script, workspace member, export, asset, or configuration entry.

### Setup action

A typed operation recommended or requested by a pack, such as ensuring dependencies, formatting, linting, analyzing, or running build generation. It is separate from desired-state declarations and subject to policy/approval.

### Command

A visible structured executable-plus-arguments operation. It cannot be hidden in a template and is subject to ownership, capabilities, policy, digest, and approval.

### Readiness action

An unresolved binding, dependency, approval, or manual integration step reported to the user. It may coexist with useful fragment output in flexible mode.

### Generation plan

The complete immutable validated description of sources, packs, plugins, files, invocations, rules, bindings, graphs, outputs, contributions, commands, approvals, and readiness before rendering.

### Artifact

One planned generated or copied output with identity, content kind, destination, lifecycle, provider facts, dependencies, and ownership.

### Ownership manifest

Writer metadata recording which pack instance/artifact owns committed paths and content digests for safe updates and cleanup.

### Lock file

`codepotg.lock`, which records immutable pack commits/digests and plugin/behavior versions for reproducibility. It never stores credentials or secrets.

## Ownership matrix

| Concern | Project | Pack | Template | Core/planner | Adapter/plugin | Host |
|---|---:|---:|---:|---:|---:|---:|
| Source/spec path | owns | may require named source | no | resolves | source adapter loads | restricts access |
| Pack selection | owns | identifies itself | no | resolves | provider fetches | restricts network/Git |
| Target language | no global choice | declares per-target defaults | owns target | resolves per file | language adapter implements | may restrict plugins |
| Template engine | no global choice | declares engine defaults | engine inferred/explicit | resolves per file | engine adapter renders | controls sandbox |
| Internal template list | no | owns | one entry | discovers/plans | no | no |
| Output root | owns instance root | declares relative/default intent | declares relative output | validates | writer commits | restricts filesystem |
| Selection | no internal details | owns | consumes | compiles | no | no |
| Binding definition | supplies value | defines/docs | declares usage | resolves | language/ecosystem renders | may restrict access |
| Rules | requests permitted overrides | sets defaults/restrictions | may set local rules | merges/provenance | owns schema/semantics | owns hard security limits |
| Dependencies | selects toolchain/policy | declares desired dependencies | no | aggregates | ecosystem adapter plans | controls execution/network |
| Commands | owns project commands/policy request | owns pack commands/setup | cannot run commands | plans/validates | executor/ecosystem resolves | final authority |
| Static files | configures output/ignore only through exposed fields | owns content/ignore | not rendered | discovers/plans | writer copies | filesystem policy |
| Barrels | supplies bindings/overrides only | owns barrel template | authors text/exports layout | supplies planned exports | language adapter renders paths/syntax | no |

## Forbidden terminology shortcuts

Agents must not say or implement:

- “the project language”;
- “the pack language” as a singular global selection;
- “a task chooses a template directory”;
- “barrels are generated automatically by core”;
- “static files need explicit emissions”;
- “the template can write files or run commands”;
- “language adapter means framework adapter”;
- “migration means v2 decodes old files”;
- “pack type” when composable integration traits are intended.
