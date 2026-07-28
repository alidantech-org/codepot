# Clean-room rewrite policy

## Purpose

The v2 implementation is a new architecture, not a refactor of the existing `packages/python/dryv` internals.

The existing package remains available for old projects while v2 is built and validated. V2 does not include old configuration decoders or old execution paths.

## Allowed use of the old package

Agents may inspect the old package to identify:

- real normalized source data required by packs;
- representative generated outputs;
- template capabilities users rely on;
- performance and scale requirements;
- diagnostics users need;
- safety bugs that v2 must avoid;
- realistic fixtures for new acceptance tests.

## Prohibited reuse

Agents must not copy or import:

- import-time rewriting or monkey patching;
- same-name module/package collisions;
- CLI `sys.path` or `sys.modules` manipulation;
- global decorator plugin registries;
- internal directory plugin scanning;
- OpenAPI-specific data leaked into target adapters;
- duplicate generation representations;
- template source scanning as hidden dependency planning;
- unsandboxed rich template contexts;
- shell-string command execution defaults;
- per-file-only transactions presented as whole-generation safety;
- layout-insensitive comparisons;
- overwritten duplicate output maps;
- mutable internals inside frozen containers.

## No compatibility runtime

V2 does not implement:

- a decoder for old `dryv.yaml` `tasks`;
- project-level `language`;
- `templateDir`;
- a `paths.yaml` parser;
- a fallback to the old generator;
- adapter wrappers around old language implementations;
- import aliases pointing to old modules.

This prevents old separation-of-concern problems from becoming permanent v2 dependencies.

## Re-authoring approach

Project migration is explicit re-authoring:

- old task input becomes a named v2 source;
- old task template directory becomes a configured pack instance;
- old output/clean/commands become pack-instance or project lifecycle fields;
- global language is removed;
- pack templates infer their own targets;
- old pack paths/emissions/folders are redesigned as `DryvPack.yaml` content, selections, patterns, files, bindings, and profiles.

The repository may contain documentation or standalone analysis tools that help authors understand old files, but the v2 runtime and package dependency graph remain clean.

## Output parity

Parity testing does not require architectural compatibility.

For each re-authored pack:

1. create a small inspectable v2 fixture;
2. create a realistic v2 fixture;
3. compare behavior and generated intent with the old pack;
4. classify differences as intentional v2 improvements or defects;
5. fix accidental differences in the new implementation;
6. never add an old runtime path solely to preserve an implementation quirk.

## Release cutover

The final release replaces the old user distribution after:

- core architecture and security tests pass;
- official adapters pass conformance suites;
- official packs generate realistic projects;
- Python, CLI, configure, Git pack, memory, and filesystem workflows pass;
- re-authoring guides are complete;
- release packaging installs batteries-included defaults.

The old source remains in repository history and may remain archived for reference, but it is not imported by the released v2 runtime.
