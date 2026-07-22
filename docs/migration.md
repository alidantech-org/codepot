---
title: Migration
description: Move existing Codepot contracts and Python generation workflows to the new packages.
order: 6
---

# Migration

## TypeScript authoring

The preferred compatibility change is import-only:

```diff
- import { z } from 'zod';
- import { defineVersionContract, schema } from 'codepot-openapi';
+ import { defineVersionContract, schema, z } from 'codepotx';
```

Do not globally rename `z` to `schema`; existing contracts may already use Codepot's `schema` helpers.

## Configuration

```diff
- package.config.ts
+ codepotx.config.ts
```

```diff
- definePackageConfig(...)
+ defineCodepotConfig(...)
```

Project outputs, template sources, cleanup, and before/after commands move to `CodepotFile.yml`.

## Python `codepotg`

The new TypeScript templating/generation layers preserve the useful Python behavior:

- `paths.yaml` selection modes and aliases;
- naming sets and classified contexts;
- partials and static/raw files;
- dependency output indexing and import facts;
- dry runs and file classifications;
- safe cleanup and reports;
- project-owned commands.

Jinja templates must be converted to Handlebars. Use `codepotx variables <task>` to inspect the available context before converting a pack.
