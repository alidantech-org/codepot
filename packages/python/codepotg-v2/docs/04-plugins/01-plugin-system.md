# Plugin system

## Goal

CodepotG v2 discovers independently installable Python plugins through standard Python entry points. Official plugins receive no hidden privileges.

## Plugin categories

Initial categories are:

- source adapters;
- language/target-syntax adapters;
- template-engine adapters;
- pack providers;
- ecosystem/toolchain adapters;
- artifact writers;
- cache stores;
- command executors;
- approval stores;
- event sinks.

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

An entry point exposes a factory, not a process-global mutable instance.

```toml
[project.entry-points."codepotg.language_adapters"]
typescript = "codepotg_language_typescript.plugin:create_plugin"
```

## Plugin descriptor

Every plugin descriptor declares:

- stable plugin ID;
- package/distribution name;
- implementation version;
- plugin API version;
- supported core and IR versions;
- aliases;
- capabilities;
- owned configuration schemas;
- factory;
- trust classification;
- documentation metadata.

## Discovery

Discovery uses `importlib.metadata.entry_points`. Core must not scan internal directories or import every module looking for decorators.

Discovery returns descriptors. Runtime instance creation happens later with an explicit immutable context.

## Registry

Registries are normal instances owned by a runtime. They validate:

- duplicate IDs;
- alias conflicts;
- incompatible API versions;
- missing capabilities;
- incompatible IR versions;
- conflicting configuration ownership;
- factory contract violations.

No module import mutates a global registry.

## Plugin context

Factories receive only explicit public services needed by their category, such as:

- diagnostic sink;
- immutable options;
- cancellation token;
- source/pack access ports;
- target syntax registry;
- controlled cache scope.

A language adapter does not receive an artifact writer or command executor because it does not own those responsibilities.

## Trust

Python plugins are executable dependencies and require the same trust as any installed Python package. Declarative packs are data and have a separate command approval boundary.

Inspection reports plugin source distribution, version, entry point, capabilities, API versions, and executable trust status.

## Failure behavior

A broken optional plugin does not corrupt the registry. Discovery reports a diagnostic identifying the distribution and entry point. Selecting that plugin fails clearly; unrelated plugins remain available.

## Conformance suites

Core publishes reusable tests for every plugin category. Official packages must run the same suite expected of third-party packages.

## Non-goals

- no hardcoded `if language == "typescript"` logic in core;
- no decorator registry;
- no internal directory scanning;
- no import-time singleton construction;
- no plugin access to private core modules.
