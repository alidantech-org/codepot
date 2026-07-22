# codepotx

`codepotx` is the active TypeScript implementation of Codepot.

Codepot combines three independent, user-owned layers to generate source code:

1. **Authoring** — a reusable `codepot.config.ts` specification.
2. **Template packs** — reusable Handlebars templates whose `paths.yml` controls emitted folders, files, names, selections, and write behavior.
3. **Consumer projects** — a project-owned `CodepotFile.yml` that combines authoring and template sources with output rules and generation tasks.

## The three layers

### Authoring: `codepot.config.ts`

The authoring layer describes the contracts and semantic information that generation consumes.

It can define information such as:

- properties and schemas;
- entities and relations;
- resources and operations;
- request and response contracts;
- access and runtime metadata;
- frontend metadata;
- OpenAPI and generator metadata.

Authoring is owned by its author and is reusable. One authored specification may be shared across several projects and used with different template packs.

Authoring sources may be local, packaged, or retrieved from a Git repository. Git-backed authoring should support a branch, tag, or commit reference and an optional path to `codepot.config.ts`.

### Template packs: `paths.yml` and Handlebars

A template pack controls what generated code looks like.

The pack owns:

- `paths.yml`;
- Handlebars templates;
- static files distributed with the pack;
- output folder and filename rules;
- semantic selections and aliases exposed to templates;
- framework and architecture conventions;
- import and dependency behavior;
- managed, immutable, and other supported write rules.

Codepot itself must not force NestJS, Flutter, React, TypeORM, SDK, folder, or naming conventions. Template authors decide those conventions.

Template packs are reusable independently from authoring. They may live locally, in Git repositories, in packages, or eventually in a template marketplace.

### Consumer projects: `CodepotFile.yml`

`CodepotFile.yml` lives in the project receiving generated code.

It is owned by that project and combines:

- an authoring source;
- a template-pack source;
- output locations;
- named generation tasks;
- cleanup rules;
- environment and working-directory rules;
- commands that run before generation;
- commands that run after generation.

The target project therefore controls its own generation lifecycle.

A task may prepare or refresh authoring before generation, clean generated locations, render a selected template pack, and then run project tools such as ESLint, Prettier, type checking, builds, or other user-defined commands.

`allow: true` is the project’s explicit permission for Codepot to execute the configured generation workflow and its commands.

## Generation flow

```text
CodepotFile.yml
        ↓
resolve the selected authoring source
        ↓
load and compile codepot.config.ts
        ↓
resolve the selected template-pack source
        ↓
load paths.yml and Handlebars templates
        ↓
plan and emit generated files
        ↓
run the project-owned after commands
```

The same authoring source can be combined with multiple template packs and consumer projects. The same template pack can also be reused with many authoring sources.

## What `codepotx` will own

The active Node.js package is intended to provide one installation and CLI for:

- TypeScript authoring through `codepot.config.ts`;
- authoring validation and OpenAPI generation;
- local, package, and Git source resolution;
- `CodepotFile.yml` loading and task execution;
- `paths.yml` interpretation;
- Handlebars template rendering;
- deterministic generation planning;
- generated-file writing and cleanup behavior;
- user-authored before and after commands;
- structured diagnostics, dry runs, and progress reporting.

The CLI will be installed as:

```bash
npm install --global codepotx
```

The exact commands and configuration schemas will be designed before implementation and must remain consistent with the three-layer ownership model above.

## Migration reference

The deprecated Python generator, `codepotg`, remains an important behavioral reference. Its task runner, command execution, `paths.yml` behavior, template contexts, imports, dependency planning, file lifecycle, cleanup, dry runs, and reporting must be evaluated and deliberately ported to TypeScript.

The active generator will use Handlebars rather than Jinja. The migration must preserve important behavior instead of treating the Python implementation as disposable example code.

## Current status

This directory is a clean restart and currently contains documentation only.

The previous Node.js authoring and OpenAPI implementation is preserved in `../codepotx-old`. No internal folder structure or runtime architecture has been committed for the new package yet; that design will be planned before implementation starts.
