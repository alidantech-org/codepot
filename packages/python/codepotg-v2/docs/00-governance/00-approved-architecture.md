# Approved CodepotG v2 architecture

This document is the highest-priority design contract for the clean rewrite under `packages/python/codepotg-v2`.

An implementation that conflicts with this document is incorrect even when it resembles the existing generator.

## Clean-room boundary

- The existing `packages/python/codepotg` package remains the complete implementation for old behavior.
- CodepotG v2 does not import old implementation modules.
- CodepotG v2 does not implement compatibility decoders for old `tasks` configuration or `paths.yaml`.
- CodepotG v2 does not preserve old internal class names, dependency direction, registries, monkey patches, CLI path manipulation, or duplicate representations.
- Existing templates and configurations may be studied to understand real generation needs, but they are re-authored into the new contracts.
- Re-authoring means expressing projects and packs through v2 schemas, not embedding the old runtime inside v2.

## Two authored configuration files

CodepotG v2 has two primary authored YAML contracts:

1. `codepotg.yaml` contains all project-owned configuration.
2. `CodepotgPack.yaml` contains all pack-owned configuration.

No additional user-edited pack configuration file is required. Pack instance configuration belongs under the matching entry in `codepotg.yaml`.

## Project ownership

`codepotg.yaml` owns:

- project identity;
- named semantic sources and specification paths;
- project toolchains and selected package managers;
- host/project command requests;
- global project before and after commands;
- ordered pack instances;
- each pack instance source, profile, output root, options, bindings, overrides, clean scopes, and project-owned commands.

The project does not select one global language. A project may generate TypeScript, Dart, YAML, Markdown, SQL, JSON, Dockerfiles, images, and other targets together.

## Pack ownership

`CodepotgPack.yaml` owns:

- pack identity and compatibility;
- content roots and Gitignore-compatible exclusions;
- named path recipes and typed path-token rules;
- source-file discovery and descriptor configuration;
- selections and invocation fan-out;
- template, barrel, static, partial, documentation, and binary roles;
- per-template bindings and dependencies;
- pack language and template-engine rules;
- pack options and documented setup inputs;
- dependency and manifest contributions;
- typed setup actions and pack-owned commands;
- lifecycle and file-ownership policy;
- manual setup instructions and pack documentation.

There is no root-level system-owned barrel subsystem. A barrel is an authored template source file with `role: barrel`.

## Template ownership of target and destination pattern

A template source file owns its target syntax and its default destination pattern.

The target convention is:

```text
file-name.{target-extension}.{template-engine-extension}
```

The destination convention is that the content-root-relative source path is parsed as a path program:

```text
{namedPathRecipe}/[typed.expression].ts.jinja
```

The final engine suffix is removed and the target suffix remains.

Examples:

```text
{models}/[model.name.kebab.s].model.ts.jinja
{clients}/client.dart.jinja
{docs}/README.md.jinja
app/[[...slug]]/page.tsx.jinja
```

`CodepotgPack.yaml` declares named recipes under `paths`. `{recipe}` expands configured path parts and may introduce selection fan-out. `[expression]` resolves a bounded typed path value.

Semantic items do not expose invented `fileName`, `filePath`, or `directory` properties. Filenames are composed from literal source-path text plus explicit typed name projections.

## Stable name projections

Named semantic items expose case projections:

```text
raw, clean, snake, kebab, camel, pascal,
screaming, constant, dot, path, lower, upper
```

Each projection exposes:

```text
o/original, s/singular, p/plural, number
```

Examples:

```text
[entity.name.pascal.s]
[resource.name.path.o]
[operation.name.camel.o]
```

Naming and inflection are deterministic, behavior-versioned, testable, and included in cache/lock behavior identity.

## Static files

Every non-template file below an emitting content root is copied by default unless ignored or classified as non-emitting documentation.

Static and binary files use the same tokenized source-path composition and may fan out through selection-bearing path recipes. Their bytes remain unchanged.

## Typed configuration boundary

Raw YAML ends inside configuration infrastructure. Application and domain services receive immutable typed models. Unknown fields are errors. Generic recursive dictionary merging is forbidden.

## Adapter boundary

- Source adapters normalize one source format directly into neutral IR.
- Language adapters implement target syntax, target filename validation, imports, exports, types, literals, comments, and locked language rules.
- Language adapters do not select output folders and do not invent semantic filename properties.
- Template-engine adapters render immutable planned contexts and do not plan destinations.
- Ecosystem adapters understand package manifests, toolchains, package managers, and typed project contributions.
- Pack providers resolve local, installed, Git, and GitHub-hosted packs.

Official and third-party adapters use the same installable Python entry-point contracts.

## Python API first

The importable Python application API is the primary interface. CLI, configure wizard, MCP, HTTP, playground, and notebook integrations are thin frontends over the same application services.

## Planning and safety

Before rendering, CodepotG resolves and validates:

- project and pack typed configuration;
- source and pack identities;
- template engine and target per source file;
- path recipes, name tokens, selection aliases, and every destination;
- bindings, dependencies, imports, providers, and artifacts;
- output ownership and collisions;
- setup actions, commands, capabilities, and approvals.

Invalid plans never call renderers or writers. Files are staged and committed transactionally with exact content comparison.

## Distribution

The release model supports:

- minimal `codepotg-core`;
- batteries-included `codepotg` installing compatible defaults;
- independently versioned source, language, engine, ecosystem, and pack distributions;
- local and Git/GitHub pack sources locked to immutable commits/digests.

## Agent rule

Every agent must read this document, the relevant detailed design, the matching task ledger, and `tasks/PARALLEL_WORK.md` before implementation. Design changes require the documented change process before code is written.
