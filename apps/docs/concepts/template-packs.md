---
title: Template packs
description: Reusable, user-owned implementation patterns for Jinja and Handlebars generation workflows.
order: 32
---

# Template packs

Template packs preserve how a team implements software: folders, filenames, imports, types, classes, framework conventions, static files, and lifecycle rules.

Codepot deliberately keeps these decisions outside the core semantic contract.

## CodepotG packs

CodepotG uses Jinja templates and `paths.yaml`.

```text
templates/typescript/
├── paths.yaml
├── _partials/
├── models/
└── services/
```

The pack receives normalized OpenAPI-derived contexts and may use CodepotG filters, aliases, dependency facts, and lifecycle policy.

## `codepotx` packs

`codepotx` uses Handlebars templates and `paths.yaml`.

```text
templates/typescript/
├── paths.yaml
├── _partials/
└── {model}/[model.name.kebab].ts.hbs
```

The templating engine compiles configuration, discovers sources, validates variables and helpers, creates descriptors, and renders with prototype access disabled.

## Common responsibilities

A pack can own:

- selection of schemas, resources, operations, or other contexts;
- local aliases such as `model` or `operation`;
- output path expressions;
- naming conventions;
- partials and reusable fragments;
- static or raw files;
- imports and dependencies;
- managed or immutable lifecycle intent;
- required variables.

## Consumer ownership

The project receiving files still controls:

- which pack is selected;
- output roots;
- project variables;
- allowed cleanup scopes;
- before and after commands;
- whether generation is enabled.

## Why packs remain separate

One contract may generate:

- backend services;
- database models;
- web or mobile SDKs;
- frontend forms;
- documentation;
- configuration;
- tests or fixtures.

Keeping architecture in packs lets the same semantic source support different stacks without making the compiler assume one framework.
