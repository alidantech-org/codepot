---
title: Codepot Lang
description: The in-progress language direction for expressing software intent clearly for developers, tools, and AI.
order: 4
---

# Codepot Lang

Codepot Lang is the larger language project behind the long-term Codepot vision.

The current `codepotx` package lets teams author contracts in TypeScript, reuse Handlebars template packs, and generate code safely today. Codepot Lang is being developed separately as a purpose-built, strongly typed language for describing software systems more directly.

## The goal

Modern software intent is spread across source files, framework decorators, configuration, database schemas, API documents, prompts, and team knowledge.

Codepot Lang aims to give that intent a clear language of its own so it can be understood by:

- developers;
- compilers and language servers;
- code generators;
- documentation and analysis tools;
- AI coding agents.

## What it is intended to express

The language direction includes concepts such as:

- typed schemas and reusable properties;
- resources and operations;
- relationships and constraints;
- access and lifecycle rules;
- generator-facing metadata;
- reusable modules and a standard library.

The exact language design is still in progress and should not be treated as a replacement for the current TypeScript workflow yet.

## How it relates to `codepotx`

The two projects share the same larger purpose: make software intent explicit and reusable.

- **Use `codepotx` now** for TypeScript authoring, template packs, project generation tasks, and safe code emission.
- **Follow Codepot Lang** for the evolving language, compiler, tooling, and editor direction.

The long-term aim is for Codepot Lang contracts to participate in the same kind of reusable generation workflows without forcing target projects to give up control of their templates or output rules.

## Project status

Codepot Lang is experimental and actively in progress. The source is available in the public `alidantech-org/codepot_lang` repository.
