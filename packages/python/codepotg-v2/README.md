# CodepotG v2

CodepotG v2 is the clean-room rewrite of the Python generation runtime. This directory currently contains the agreed architecture, migration plan, package boundaries, task tracking, and empty implementation placeholders.

The existing `packages/python/codepotg` package remains untouched and serves only as a behavior and migration reference. New implementation must not import its internal modules or reproduce its global registries, raw YAML processing, CLI-centered logic, OpenAPI leakage, or overlapping emission paths.

## Primary goals

- Make the importable Python application API the primary interface.
- Keep the CLI, servers, playgrounds, and MCP tools as thin adapters.
- Replace raw configuration dictionaries with immutable typed contracts.
- Treat `codepotg.yaml` as project orchestration and `CodepotgPack.yaml` as the complete pack contract.
- Let every template own its target language through `name.<target>.<engine>` detection.
- Support heterogeneous packs containing code, configuration, documentation, and static files.
- Discover source, language, template-engine, and pack plugins through normal Python packages and entry points.
- Plan every output and dependency before rendering, then commit outputs transactionally.
- Preserve compatibility through explicit legacy decoders and migrations rather than contaminating the new design.

## Documentation

Start with [`docs/README.md`](docs/README.md). The complete staged implementation backlog is in [`docs/tasks/00-master-plan.md`](docs/tasks/00-master-plan.md), and progress is recorded in [`docs/tasks/PROGRESS.md`](docs/tasks/PROGRESS.md).

## Status

Documentation and directory scaffold only. No runtime implementation or packaging metadata has been added yet.
