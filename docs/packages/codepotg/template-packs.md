---
title: Template packs
description: Structure reusable CodepotG packs with paths configuration, Jinja templates, partials, raw files, and lifecycle policy.
product: codepotg
package: codepotg
order: 6
---

# Template packs

A template pack owns how normalized software intent becomes project code.

It should preserve a real project's frameworks, folder layout, naming, imports, validation style, and implementation conventions instead of generating one generic architecture.

## Pack structure

```text
templates/typescript/
├── paths.yaml
├── models/
│   └── model.ts.j2
├── dtos/
│   └── dto.ts.j2
├── services/
│   └── service.ts.j2
├── barrels/
│   └── index.ts.j2
├── partials/
│   └── field.ts.j2
└── static/
    └── .gitignore
```

`paths.yaml` decides what is rendered and where. Jinja files decide the contents.

## Pack selection in a task

```yaml
tasks:
  sdk:
    input: ./openapi.json
    language: typescript
    templateDir: ./templates/typescript
    output: ./generated/sdk
```

Without `templateDir`, CodepotG resolves the bundled pack for the selected language.

## Two compatible planning models

### Graph packs

New packs should prefer:

- named `selections`;
- named `emissions`;
- explicit providers and provided facts;
- grouped emissions;
- barrels;
- bounded template contexts.

Graph packs make dependencies visible and keep memory bounded.

### Legacy folder packs

Existing `folders` recipes remain supported. They receive the established compatibility context and are useful while a project migrates.

New features should be designed for graph packs first unless compatibility requires legacy behavior.

## Templates and partials

Templates normally use `.j2`. Pack configuration can define the template extension and whether it is stripped from output names.

Partials and macros should hold repeated rendering logic, not business selection logic. Selection belongs in `paths.yaml` so planning remains inspectable.

## Raw and static files

A pack can copy files without Jinja rendering when raw files are enabled. Use this for exact assets such as:

- `.gitignore`;
- formatter configuration;
- static boilerplate;
- binary-safe or non-template text.

Do not mark a file raw merely to avoid fixing an incorrect template context.

## Language adapters

The task language selects helpers for types, identifiers, imports, literals, files, comments, validation, frameworks, and packages.

A custom pack can use a bundled language adapter while replacing all templates.

## Pack ownership

Keep project-specific packs in the consuming repository when they encode application architecture. Publish a reusable pack only when its conventions and compatibility policy are intentionally shared.

## Versioning

Version a pack when changes can alter:

- output paths;
- file ownership;
- exported names;
- template variables;
- import behavior;
- framework APIs;
- cleanup policy.

Review generation plans before upgrading a pack.

## Recommended workflow

```bash
codepotg paths ./templates/typescript
codepotg generate sdk --dry-run --verbose
codepotg generate sdk
```

## Design principles

- Keep selection and scheduling in `paths.yaml`.
- Keep formatting and target syntax in Jinja.
- Depend on normalized variables before `raw` source access.
- Declare providers instead of reaching across unrelated render contexts.
- Use barrels only after their member emissions are planned.
- Keep lifecycle roots narrow and package-owned.