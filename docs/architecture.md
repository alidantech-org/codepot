---
title: Three-layer model
description: Understand how contracts, templates, and consumer tasks divide ownership in Codepot.
order: 3
---

# The three-layer model

Codepot separates **what the software means**, **how code should look**, and **where generation should run**.

This separation makes contracts and templates reusable without taking control away from the project that receives generated code.

## 1. Typed contracts

The authoring file is normally `codepotx.config.ts`.

It describes reusable software intent in TypeScript, including resources, schemas, fields, operations, relationships, access rules, and frontend information.

```ts
import { defineCodepotConfig, schema } from 'codepotx';

export default defineCodepotConfig({
  project: { name: 'rescue-platform' },
  contracts: [v1],
});
```

A contract should describe the software rather than a single framework-specific folder structure. One contract can therefore support several target applications.

## 2. Template packs

A template pack combines `paths.yaml` with Handlebars files.

```text
templates/typescript/
├── paths.yaml
├── _partials/
└── {model}/[model.name.kebab].ts.hbs
```

The template author owns implementation style: filenames, folders, imports, class shapes, framework conventions, and reusable partials.

The same contract can be rendered through a NestJS pack, a Flutter pack, a plain TypeScript SDK pack, a documentation pack, or any other template set.

## 3. Consumer tasks

`CodepotFile.yml` belongs to the project receiving generated files.

```yaml
allow: true

tasks:
  sdk:
    authoring: ./codepotx.config.ts
    templates: ./templates/typescript
    output: ./src/generated
    transactional: true
```

The consumer project decides:

- which contract source to use;
- which template pack to use;
- where generated files are written;
- which project variables templates receive;
- which safe cleanup roots are allowed;
- which formatting, type-checking, or validation commands run.

## Why ownership stays clear

| Layer | Owner | Main responsibility |
|---|---|---|
| Typed contract | domain or API author | Describe reusable software intent |
| Template pack | framework or architecture author | Preserve approved implementation patterns |
| Consumer task | target project | Control output, automation, and permissions |

No target project is forced to accept a particular framework or directory structure. It chooses the template pack and generation task itself.

## Why AI benefits

AI agents can read the contract to understand intent and the template pack to understand implementation conventions. They do not need to infer those decisions independently on every task.

This makes generated and AI-assisted code more predictable, reduces repeated repository exploration, and gives reviewers clear source material for checking whether a change follows the intended model.
