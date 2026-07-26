# Adapter and infrastructure plugin system

## Goal

CodepotG v2 discovers independently installable Python adapters/infrastructure packages through standard Python entry points. Official packages receive no hidden privileges.

The plugin system extends supported inputs, target validation/path behavior, template engines, pack locations, project ecosystems, writers, caches, executors, approvals, and event sinks. It does not extend application semantics.

## Categories

Initial categories are:

- source adapters;
- target/language validation and path adapters;
- template-engine adapters;
- pack providers;
- ecosystem/toolchain adapters;
- artifact writers;
- cache stores;
- command executors;
- approval stores;
- event sinks.

There is no facet-module, semantic-node, selector-provider, expression-root, context-provider, or generated-syntax-renderer category.

## Entry points

Recommended groups:

```text
codepotg.source_adapters
codepotg.language_adapters
codepotg.template_engines
codepotg.pack_providers
codepotg.ecosystem_adapters
codepotg.artifact_writers
codepotg.cache_stores
codepotg.command_executors
```

An entry point exposes a factory/descriptor rather than a process-global mutable instance.

```toml
[project.entry-points."codepotg.language_adapters"]
typescript = "codepotg_language_typescript.plugin:create_plugin"
```

## Descriptor

Every descriptor declares:

- stable plugin ID;
- package/distribution name;
- implementation and behavior versions;
- plugin API version;
- supported core and IR versions;
- aliases;
- actual capabilities;
- bounded owned configuration schemas;
- factory;
- trust classification;
- documentation metadata.

Descriptors may own configuration only for their approved category boundary. A descriptor is invalid if it claims ownership of semantic objects, schema kinds, relationships, facets, selectors, expression roots, template-context values, or generated source-code syntax.

## Discovery

Discovery uses `importlib.metadata.entry_points`. Core must not scan internal directories or import every module looking for decorators.

Discovery returns immutable descriptors. Runtime instance creation happens later with an explicit least-authority context.

## Registry

Registries are normal instances owned by a runtime/session. They validate:

- duplicate IDs and aliases;
- incompatible API/core/IR/behavior versions;
- missing/conflicting capabilities;
- conflicting configuration ownership;
- forbidden semantic/syntax ownership;
- factory contract violations.

No module import mutates a global registry.

## Plugin context

Factories receive only explicit public services needed by their category, such as:

- diagnostic sink;
- immutable typed options;
- cancellation token;
- controlled source/pack access ports;
- closed-kernel construction contract for source adapters;
- immutable planned target/path descriptors;
- controlled cache scope.

A target adapter does not receive an artifact writer, command executor, semantic registry, or source-code emitter. An engine does not receive destination-writing authority. A source adapter does not receive templates or output services.

## Closed-kernel boundary

Core alone defines and versions:

```text
semantic objects and relationships
schema kinds and controlled roles
known facets and attachment locations
root-first selectors
expression roots/properties
template-context properties
semantic validation
```

Adapters translate into or consume those contracts. Unknown source metadata may use bounded documented provenance/raw/extension values only; plugins cannot turn it into new semantics.

The implementation may be graph-shaped internally, but plugins do not receive a generic node/edge/fact extension API.

## Generated-syntax boundary

Templates, macros, partials, and static files own every emitted character.

Target adapters may detect suffixes, validate filenames/candidate identifiers, and calculate/validate target-aware module/path facts. They cannot emit types, literals, comments, imports, exports, annotations, validators, formatting, or framework code.

Template-engine adapters render already authored text from immutable prepared contexts and cannot inject target syntax or add outputs.

## Trust

Installed Python plugins are executable dependencies and require the same trust as any Python package. Declarative packs are data, with a separate approval boundary for exact commands.

Inspection reports distribution, version, entry point, capabilities, API/behavior compatibility, configuration ownership, and executable trust status.

Downloaded packs cannot install or activate Python plugins implicitly.

## Failure behavior

A broken optional plugin does not corrupt the registry. Discovery reports a diagnostic identifying the distribution and entry point. Selecting that plugin fails clearly; unrelated capabilities remain available.

A plugin requesting forbidden semantic or syntax ownership fails descriptor validation before instance creation.

## Conformance suites

Core publishes reusable tests for every category. Official packages run the same suites expected of third-party packages, including negative closed-kernel and non-rendering boundary tests.

## Non-goals

- no hardcoded target implementation branches in core;
- no open semantic/facet/selector extension system;
- no graph-query plugin surface;
- no target source-code renderer service;
- no decorator/global registry;
- no internal directory scanning;
- no import-time singleton construction;
- no private-core access.
