---
title: Guides
description: Task-oriented paths for the supported prototype workflow, the official JavaScript runtime, and future frontend integrations.
order: 40
---

# Guides

Choose a guide based on the result you need.

## Generate from typed OpenAPI contracts

Use [Prototype workflow](/docs/prototype-workflow) to:

1. author contracts with `codepot-openapi`;
2. emit OpenAPI JSON or YAML;
3. configure `Codepotg.yaml`;
4. select bundled or custom Jinja packs;
5. preview and generate safely.

This is the most mature workflow for real projects today.

## Evaluate the official JavaScript rewrite

Use [codepotx workflow](/docs/codepotx-workflow) to:

1. create `codepotx.config.ts`;
2. create a Handlebars pack and `paths.yaml`;
3. bind them through `CodepotFile.yml`;
4. inspect variables and plans;
5. generate through the runtime or `codepotx-cli`.

## Build another interface

Use [Build a runtime frontend](/docs/build-runtime-frontend) when implementing a web UI, editor command, MCP server, desktop tool, or embedded application around `codepotx`.

## Plan migration

Use [Migration strategy](/docs/migration) to compare workflows without incorrectly treating supported prototypes as already replaced.
