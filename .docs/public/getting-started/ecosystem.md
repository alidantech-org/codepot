---
title: Ecosystem and status
description: Active Dryv components, applications, and frozen earlier packages.
---

# Ecosystem and status

Repository location does not imply active development.

## Active Dryv packages

- `dryv` — Runtime IR, validation, transport, planning, plugins, inspection, and safe generation.
- `dryv-author` — typed Python authoring compiled into Runtime IR.
- `dryv-cli` — terminal frontend over public runtime operations.
- `dryv-template-jinja` — bounded Jinja template-engine adapter.
- `dryv-language-typescript` — TypeScript target facts and validation.
- `dryv-language-dart` — Dart target facts and validation.

## Active applications

- `apps/site` — public website and current documentation renderer.
- `apps/docs` — dedicated documentation application boundary.

## Frozen packages

- `packages/python/codepotg`
- `packages/nodejs/codepot-openapi`
- `packages/nodejs/codepotx`
- `packages/nodejs/codepotx-cli`

Frozen packages are retained for existing users and historical comparison. They receive no feature work, redesign, or routine modernization.

## Archived material

Everything under `.archives/**` is read-only historical evidence and must not become a dependency of active code.
