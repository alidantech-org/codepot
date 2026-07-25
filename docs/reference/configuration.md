---
title: Configuration reference
description: Understand which configuration file belongs to each Codepot package and platform generation.
order: 51
---

# Configuration reference

Do not interchange configuration filenames between engines. Each file has a distinct owner.

## `codepot-openapi`

The TypeScript package loads an authored package configuration, commonly from a project TypeScript entrypoint.

```ts
export default definePackageConfig({
  contracts: [v1],
  output: {
    folder: 'openapi',
    filePrefix: 'openapi',
    formats: ['json', 'yaml'],
  },
});
```

## `Codepotg.yaml`

Owned by the Python CodepotG generator.

```yaml
allow: true

tasks:
  sdk:
    input: ./openapi.json
    language: typescript
    output: ./generated/sdk
```

CodepotG intentionally rejects `CodepotFile.yml` and `CodepotFile.yaml`.

## `codepotx.config.ts`

Owned by `codepotx` authoring.

```ts
export default defineCodepotConfig({
  contracts: [v1],
  validation: {
    enabled: true,
    failOnWarnings: false,
  },
});
```

It describes authored contracts and validation—not consumer output paths or project commands.

## `CodepotFile.yml`

Owned by the project consuming `codepotx` generation.

```yaml
allow: true

tasks:
  sdk:
    authoring: ./codepotx.config.ts
    templates: ./templates/typescript
    output: ./src/generated
    clean: [models]
    transactional: true
```

It controls sources, tasks, outputs, variables, cleanup scopes, commands, and permission to generate.

## `paths.yaml`

Owned by a template pack in both generator families, though supported syntax and rendering engines differ.

- CodepotG uses Jinja templates and its normalized contexts.
- `codepotx` uses Handlebars templates and its variable catalog.

Do not assume a pack is portable without comparing syntax and context contracts.

## `Codepot.toml`

Owned by Codepot Lang and the final Rust platform.

```toml
[project]
name = "example"
language-version = "0.3"

[packages]
app = "src/app"

[standard-library]
mode = "embedded"

[compiler]
entry = "src/app/main.codepot"
output = ".codepot/app.ir.yaml"
```

It controls language project roots, standard-library mode, compiler entry/output, and formatter behavior.
