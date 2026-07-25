---
title: codepotg
description: Complete documentation for the stable Python and Jinja OpenAPI generation runtime.
product: codepotg
package: codepotg
order: 1
---

# `codepotg`

`codepotg` is the stable Python and Jinja generation runtime in the Codepot ecosystem.

It consumes OpenAPI 3.0 or 3.1 JSON/YAML, builds an indexed source cache, normalizes schemas and application metadata, plans files through a template pack, renders Jinja templates, and applies guarded project writes.

## Package status

- PyPI package: `codepotg`
- current package version: `1.0.0`
- Python: 3.11 or newer
- binary: `codepotg`
- template engine: Jinja 3
- input: OpenAPI 3.0 or 3.1 JSON/YAML
- bundled targets: TypeScript, Next.js, Dart, and debug packs

CodepotG is active and supported. It remains the mature generator while equivalent behavior is stabilized in `codepotx`.

## What CodepotG owns

- JSON streaming and indexed JSONL caches;
- cached YAML-to-canonical-JSON compatibility conversion;
- normalized contract and dependency inference;
- legacy and graph-based `paths.yaml` planning;
- Jinja templates, partials, filters, and raw files;
- language adapters and target helpers;
- managed and immutable lifecycle policies;
- dry runs, guarded cleanup, before/after commands, and diagnostics;
- atomic writes and generation reports;
- optional memory tracing.

## Learning path

1. [Install and run a first task](/docs/packages/codepotg/getting-started)
2. [Understand the generation pipeline](/docs/packages/codepotg/architecture)
3. [Configure `Codepotg.yaml`](/docs/packages/codepotg/configuration)
4. [Use tasks and CLI commands](/docs/packages/codepotg/tasks-cli)
5. [Build a template pack](/docs/packages/codepotg/template-packs)
6. [Write `paths.yaml`](/docs/packages/codepotg/paths-yaml)
7. [Write Jinja templates](/docs/packages/codepotg/jinja-templates)
8. [Understand the template context](/docs/packages/codepotg/template-context)
9. [Browse variable reference groups](/docs/packages/codepotg/template-variables)
10. [Understand OpenAPI preservation](/docs/packages/codepotg/openapi-normalization)
11. [Configure lifecycle safety](/docs/packages/codepotg/lifecycle-safety)
12. [Tune performance and memory](/docs/packages/codepotg/performance)
13. [Apply best practices](/docs/packages/codepotg/best-practices)

## Basic workflow

```text
OpenAPI JSON/YAML
      ↓ indexed source cache
normalized generation graph
      ↓ paths.yaml selections and emissions
bounded Jinja context
      ↓ render in memory
planned generated files
      ↓ lifecycle and safety checks
atomic project writes
```

Continue with [Getting started](/docs/packages/codepotg/getting-started).