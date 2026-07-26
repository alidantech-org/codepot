# Approved CodepotG v2 architecture

This document is the highest-priority design contract for the clean rewrite under `packages/python/codepotg-v2`.

An implementation that conflicts with this document is incorrect even when it resembles the existing generator.

## Clean-room boundary

- The existing `packages/python/codepotg` package remains the complete reference implementation for the old behavior.
- CodepotG v2 does not import old implementation modules.
- CodepotG v2 does not implement compatibility decoders for old `tasks` configuration or `paths.yaml`.
- CodepotG v2 does not preserve old internal class names, dependency direction, registries, monkey patches, CLI path manipulation, or duplicate representations.
- Existing templates and configurations may be studied to understand real generation needs, but they must be re-authored into the new contracts.
- Migration means re-authoring projects and packs into the v2 schemas, not embedding the v1 runtime inside v2.

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
- host and project command policy;
- global project before and after commands;
- ordered pack instances;
- each pack instance source, output root, options, bindings, overrides, clean scopes, and project-owned commands.

The project does not select one global language. A project and a pack may contain TypeScript, Dart, YAML, Markdown, SQL, JSON, Dockerfiles, images, and other targets together.

## Pack ownership

`CodepotgPack.yaml` replaces the conceptual responsibilities previously placed in `paths.yaml`. It owns:

- pack identity and compatibility;
- content roots and Gitignore-compatible ignore rules;
- file and folder-pattern discovery;
- selections and invocation fan-out;
- template, barrel, static, partial, documentation, and binary-file roles;
- per-template bindings and dependencies;
- pack language rules and template-engine rules;
- pack options and documented setup inputs;
- dependency and manifest contributions;
- typed setup actions and pack-owned commands;
- lifecycle and file-ownership policy;
- manual setup instructions and pack documentation.

There is no root-level system-owned `barrels` subsystem. A barrel is an authored template file with `role: barrel`.

## Template ownership

A template file is the unit that owns its target language or syntax.

The default convention is:

```text
file-name.{target-extension}.{template-engine-extension}
```

Examples:

```text
user.entity.ts.jinja
client.dart.jinja
openapi.yaml.jinja
README.md.jinja
```

The template engine is inferred from the final known suffix. The target syntax is inferred from the preceding known suffix using longest-known-suffix matching. Ambiguous files such as `Dockerfile.jinja` may declare an explicit target in `CodepotgPack.yaml`.

Language is never selected globally in `codepotg.yaml` and never assumed to be singular for a pack.

## Unified pack file model

Every discovered pack content file receives exactly one descriptor.

- Recognized template-engine suffix: render as a template unless configured as a partial.
- No template-engine suffix: copy as a static text or binary file by default.
- `role: barrel`: render an authored barrel template using planned export information.
- `role: partial`: make available to the template engine but never emit directly.
- Explicit file configuration modifies the discovered descriptor; it does not schedule a duplicate emission.
- Different source descriptors may not silently produce the same output path.

Static files are emitted by default because complete packs often contain `.gitignore`, `.env.example`, licenses, images, fixture data, Makefiles, Dockerfiles, and other unchanged content.

## Selections and output granularity

Templates and static files may run:

- once;
- once for each selected record;
- once for each group;
- once for an aggregate collection;
- through folder-pattern fan-out;
- with multiple explicitly declared named outputs.

A single aggregate template may generate all code into one file. A pack may also offer modular and monolithic profiles.

## Bindings

Packs publish a typed binding catalog. Individual templates explicitly declare which binding IDs they consume.

Bindings may represent:

- imports and symbols;
- project paths;
- package imports;
- namespaces;
- barrels and default barrels;
- text and text files;
- configuration values;
- package names;
- artifact references.

The project supplies binding values under the configured pack instance in `codepotg.yaml`. Templates refer only to logical binding IDs.

A project may bind many symbols to one barrel. Language adapters deduplicate and render the resulting imports.

Missing bindings can prompt, use a visible placeholder, omit optional behavior, skip affected templates, or fail. Flexible local generation and strict CI readiness are separate policies.

## Rules and overrides

CodepotG core owns the rule and override protocol. Adapters do not invent arbitrary merge behavior.

Every configurable rule field declares:

- typed value model;
- default value;
- merge policy;
- whether it can be overridden;
- security classification;
- documentation and schema metadata.

Supported merge operations include replace, append, prepend, union, merge-by-key, remove, reset-to-default, and not-overridable.

Rule precedence is deterministic:

1. adapter defaults;
2. pack rules;
3. template-local rules;
4. project global overrides;
5. project pack-instance overrides;
6. project template-specific overrides.

A pack may restrict adapter-allowed overrides further. A project may never loosen adapter, pack, user, or host restrictions.

## Commands and setup

Packs may contain before and after setup actions or commands so they can produce polished output, including formatting, unused-import fixes, dependency installation, validation, and code generation helpers.

Commands must be declared in `CodepotgPack.yaml`; templates cannot execute hidden commands.

Trust defaults:

- trusted local project commands: allowed by the normal local policy;
- downloaded pack commands: require approval by default;
- server, playground, and MCP environments: commands denied by default;
- host policy always wins and cannot be weakened by project or pack configuration.

Approvals are tied to the exact pack source, resolved commit, manifest digest, command digest, executable, arguments, working directory, and requested capabilities.

Typed actions are preferred over raw commands. Desired manifest changes are declared separately from commands that realize them.

## Pack traits

Packs are described by composable traits rather than one restrictive type. A pack may combine any of these characteristics:

- creates a complete runnable project;
- owns a standalone folder or package;
- contributes files to an existing project;
- requires dependencies;
- requires project bindings;
- produces fragments that need manual integration;
- owns a package manifest;
- contributes typed changes to a user-owned manifest.

Missing host integration does not automatically invalidate fragment generation. Results can be generated with warnings and explicit remaining actions.

## Plugin packages

Official and third-party plugins use the same public plugin API and Python entry-point discovery.

Initial independently installable packages are:

- `codepotg-openapi`;
- `codepotg-language-typescript`;
- `codepotg-language-dart`;
- `codepotg-template-jinja`;
- `codepotg-pack-typescript-sdk`;
- `codepotg-pack-dart-sdk`;
- `codepotg-pack-flutter-sdk`.

Language adapters implement target syntax, identifiers, types, literals, imports, exports, comments, naming, and typed language rules. They do not load sources, select templates, write files, run commands, or own framework architecture.

Template-engine adapters implement parsing, rendering, includes, sandboxing, engine-specific rules, and immutable context handling. They do not own target-language behavior or output planning.

## Python-first product interface

The importable Python application API is the primary interface.

The CLI, configure wizard, MCP tools, HTTP services, playgrounds, and notebooks are adapters over the same application services. Business logic must not live in CLI command handlers.

The core must support filesystem and in-memory generation, structured diagnostics, progress events, cancellation, sync and async execution, and server-safe policies.

## Distribution

The normal `codepotg` distribution is batteries included and installs compatible official defaults. A minimal core distribution remains available for embedded and custom installations.

Git and GitHub are the first pack distribution mechanism. Public and private repositories use the user's existing Git credentials. Resolved commits and digests are recorded in `codepotg.lock`.

## Implementation quality

- Immutable typed models at application boundaries.
- No raw YAML dictionaries below the configuration infrastructure.
- No mutable global registries.
- No import-time plugin registration side effects.
- No template source scanning to infer hidden dependencies.
- No direct template filesystem writes or shell execution.
- Complete planning and validation before rendering.
- Whole-generation transactional writes.
- Exact content comparison rather than layout-insensitive comparison.
- Small unit tests, reusable conformance suites, and inspectable integration fixtures.
