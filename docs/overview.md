---
title: Codepot overview
description: Give developers and AI agents a shared, reusable source of truth for building software.
order: 1
---

# Codepot

Codepot helps teams describe important software decisions once and reuse them whenever code is created or changed.

Instead of asking every developer or AI agent to rediscover your naming, routes, models, folder structure, and coding patterns, Codepot keeps that intent in three clear layers.

## The three layers

1. **Typed contracts** describe what the software means: resources, fields, operations, relationships, access rules, and other reusable facts.
2. **Template packs** describe how your team turns those facts into code for a particular language, framework, or project style.
3. **Consumer tasks** live in each target project and decide which contracts and templates to use, where files belong, and which project commands should run.

Each layer can evolve independently. The same contract can generate several applications, and the same template pack can be reused across several products.

## Why this matters for AI coding

AI is most useful when it has reliable context. Without that context, it spends tokens reading the same repository repeatedly, invents slightly different patterns, and can drift away from decisions your team already made.

Codepot gives AI agents the same explicit contract and templates that developers review. This helps them:

- understand the intended software model before editing code;
- reuse approved project patterns instead of improvising them;
- generate repetitive files consistently;
- make smaller, easier-to-review changes;
- avoid silently changing naming or architecture between features.

## A simple workflow

```text
codepotx.config.ts
        +
reusable Handlebars template pack
        +
project-owned CodepotFile.yml
        ↓
validated plan and generated source code
```

You can inspect the available template variables, preview the generation plan, run a dry run, and then generate files into the target project.

## The larger Codepot direction

The TypeScript package, `codepotx`, is the practical way to use Codepot today.

Codepot Lang is a larger language project currently in progress. Its goal is to make software intent easier to express in a strongly typed, purpose-built language that developers, compilers, tools, and AI agents can all understand. Codepot Lang does not replace the current TypeScript workflow yet; it extends the long-term vision behind it.
