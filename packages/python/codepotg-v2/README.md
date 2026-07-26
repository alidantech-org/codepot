# CodepotG v2

CodepotG v2 is the clean-room rewrite of the Python generation runtime. This directory contains the approved architecture, implementation stages, package boundaries, detailed task tracking, and empty implementation placeholders.

The existing `packages/python/codepotg` package remains untouched and serves only as a source of real requirements and representative outputs. New implementation must not import its internals or reproduce its global registries, raw YAML processing, CLI-centered logic, OpenAPI leakage, overlapping emission paths, or old configuration runtime.

## Primary goals

- Make the importable Python application API the primary interface.
- Keep the CLI, servers, playgrounds, notebooks, and MCP tools as thin adapters.
- Replace raw configuration dictionaries with immutable typed contracts.
- Treat `codepotg.yaml` as project orchestration and `CodepotgPack.yaml` as the complete pack contract.
- Let every template own its target syntax through `name.<target>.<engine>` detection.
- Support heterogeneous packs containing code, configuration, documentation, static files, and binary assets.
- Discover source, language, template-engine, ecosystem, pack-provider, writer, cache, and command plugins through normal Python packages and entry points.
- Plan every output, import, binding, dependency, command, and contribution before rendering.
- Commit filesystem output transactionally and support memory/archive writers.
- Re-author projects and packs into the v2 schemas without embedding old decoders or execution paths.

## Documentation

Start with [`docs/README.md`](docs/README.md), then read the approved architecture and agent rules. The implementation backlog is in [`docs/tasks/00-master-plan.md`](docs/tasks/00-master-plan.md), parallel ownership is in [`docs/tasks/PARALLEL_WORK.md`](docs/tasks/PARALLEL_WORK.md), and evidence is recorded in [`docs/tasks/PROGRESS.md`](docs/tasks/PROGRESS.md).

## Status

Documentation and directory scaffold only. No runtime implementation or packaging metadata has been added yet.
