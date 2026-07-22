# Codepot

Codepot is a user-controlled authoring and code-generation system.

It lets people describe reusable software contracts once, combine them with reusable template packs, and generate source code into one or many consumer projects. The specification author, template author, and target project each retain control over their own part of the process.

## Core model

Codepot is built around three separate layers.

### 1. Authoring source

```text
codepot.config.ts
```

The authoring layer is currently written in TypeScript. It defines the contracts and semantic information that generators consume, including schemas, entities, resources, operations, access metadata, frontend metadata, OpenAPI information, and other generator-facing facts.

Authoring is reusable and shareable. A single authoring source can generate different outputs for different projects by being combined with different template packs and task rules.

An authoring source may be local, packaged, or resolved from a Git repository using a branch, tag, or commit reference.

### 2. Template pack

```text
paths.yml
*.hbs
```

A template pack determines how authored information becomes source code.

`paths.yml` controls the emitted folders, files, filenames, context selections, aliases, and supported write behavior. Handlebars templates control the contents of generated files. Static files may also be distributed as part of a pack.

Template packs own framework and architecture decisions. Codepot must not force a specific backend framework, frontend framework, ORM, SDK structure, naming convention, or folder structure.

Template packs are reusable independently from authoring and may be shared locally, through Git, through packages, or through a future template marketplace.

### 3. Consumer project

```text
CodepotFile.yml
```

`CodepotFile.yml` lives in the project receiving generated code. It combines an authoring source, a template-pack source, output rules, and named generation tasks.

The consumer project controls:

- where authoring comes from;
- where templates come from;
- where generated files are written;
- which paths may be cleaned;
- commands that run before generation;
- commands that run after generation;
- command working directories and environment values;
- optional and required project automation.

Commands are a first-class part of Codepot. They allow the target project to refresh contracts, format generated files, remove unused imports, type-check output, build code, or run any other user-defined workflow. `allow: true` is the project’s explicit permission to execute its configured generation tasks and commands.

## How generation works

```text
CodepotFile.yml
        ↓
resolve authoring source
        ↓
load and compile codepot.config.ts
        ↓
resolve template-pack source
        ↓
load paths.yml and Handlebars templates
        ↓
plan and emit generated files
        ↓
run project-owned after commands
```

This separation allows:

- one authoring source to generate into many projects;
- one authoring source to use many architecture-specific template packs;
- one template pack to work with many authored specifications;
- each consumer project to control its own output, cleanup, and command lifecycle;
- authoring and template sources to be shared through local paths, packages, or Git repositories.

## Repository status

This repository is being restarted around the three-layer model above.

### `packages/nodejs/codepotx`

The active TypeScript implementation.

It is intended to provide one npm package and CLI for TypeScript authoring, OpenAPI generation, source resolution, `CodepotFile.yml` tasks, `paths.yml`, Handlebars generation, file emission, cleanup, dry runs, diagnostics, and user-authored commands.

The package now contains its modern pnpm, Turbo, TypeScript, tsdown, packaging, and validation foundation plus a minimal `src/index.ts`. Its internal feature architecture remains intentionally unplanned until the next design step.

The public schema API will be owned by Codepot. Users will import builders such as `schema` from `codepotx`; Zod remains an internal dependency and is not exposed as a peer dependency or authoring requirement.

### `packages/nodejs/codepotx-old`

The preserved previous Node.js authoring and OpenAPI implementation.

It remains available as reference code while the new `codepotx` direction is designed and implemented. New work should not be added there unless it is specifically required for migration analysis.

### `packages/python/codepotg`

The deprecated Python and Jinja generator.

It is no longer the supported implementation, but it remains an important behavioral reference for generation tasks, command execution, `paths.yml`, template contexts, language adaptation, imports, dependency planning, write lifecycle, cleanup, dry runs, and reporting.

Its package and command identity is `codepotg`. New users should use the Node.js `codepotx` direction once it becomes available.

### `codepot_lang`

The separate Rust language and compiler project remains the most ambitious long-term language direction. It is experimental and does not replace the active TypeScript authoring and generation restart in this repository.

## Guiding principles

- Users own their authoring source.
- Template authors own generated architecture and source style.
- Consumer projects own output rules and automation commands.
- Authoring and templates must remain independently reusable.
- Local, package, and Git-backed sources are part of the intended model.
- `paths.yml` is the template pack’s source of output structure.
- `CodepotFile.yml` is the consumer project’s generation binding and task runner.
- Handlebars is the active template direction for the Node.js generator.
- The deprecated Python generator must be studied and migrated carefully rather than discarded.
- The new package structure and implementation architecture will be planned before feature code is added.

## License

MIT
