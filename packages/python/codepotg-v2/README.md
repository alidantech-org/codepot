# CodepotG v2

CodepotG v2 is the clean-room rewrite of the Python generation runtime. This directory contains the approved closed semantic kernel, project/pack contracts, adapter boundaries, implementation stages, package task tracking, and empty implementation placeholders.

The existing `packages/python/codepotg` package remains untouched and serves only as a source of real requirements and representative outputs. New implementation must not import its internals or reproduce its global registries, raw YAML processing, CLI-centered logic, OpenAPI leakage, overlapping emission paths, or old configuration runtime.

## Primary goals

- Make the importable Python application API the primary interface.
- Keep CLI, servers, playgrounds, notebooks, IDE, and MCP tools as thin adapters.
- Replace raw configuration dictionaries with immutable typed contracts.
- Maintain a closed, typed, versioned semantic kernel owned only by core.
- Model groups, structural schemas, operations, views, storage mappings, policies, events, workflows, and known facets through clear typed relationships.
- Use fixed root-first selectors and outer-to-inner template contexts.
- Treat `codepotg.yaml` as project orchestration and `CodepotgPack.yaml` as the pack contract.
- Let templates, macros, partials, and static files own every emitted character.
- Use target adapters only for suffix detection, target validation, and module/path facts.
- Support heterogeneous packs containing code, configuration, documentation, static files, and binary assets.
- Discover source, target, template-engine, ecosystem, pack-provider, writer, cache, and command adapters through normal Python packages and entry points without allowing semantic extension.
- Plan every semantic reference, artifact identity, output, symbol, dependency, binding, command, approval, and impact relationship before rendering.
- Explain artifacts and provide deterministic dry-run/blast-radius information.
- Commit filesystem output transactionally and support memory/archive writers.
- Prove deterministic full generation before conservative incremental generation.
- Re-author projects and packs into v2 without embedding old decoders or execution paths.

## Non-goals

- arbitrary third-party semantic objects, facets, selectors, or graph-query DSLs;
- neutral `resource`, `model`, `entity`, `frontend`, or `ui` roots;
- language adapters that render types, literals, imports, exports, comments, validators, decorators, or framework syntax;
- hidden pack profiles, `filePatterns`, or explicit ordinary-file registries;
- generated output hashes in the dependency lock.

## Documentation

Start with [`docs/README.md`](docs/README.md), [`docs/00-governance/00-approved-architecture.md`](docs/00-governance/00-approved-architecture.md), and [`docs/00-governance/04-closed-semantic-kernel.md`](docs/00-governance/04-closed-semantic-kernel.md).

The implementation backlog is in [`docs/tasks/00-master-plan.md`](docs/tasks/00-master-plan.md), parallel ownership is in [`docs/tasks/PARALLEL_WORK.md`](docs/tasks/PARALLEL_WORK.md), and evidence is recorded in [`docs/tasks/PROGRESS.md`](docs/tasks/PROGRESS.md).

## Status

Documentation and directory scaffold only. Runtime implementation and packaging metadata have not started.
