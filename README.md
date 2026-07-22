# Codepot

Codepot gives developers and AI agents a shared, reusable source of truth for building software.

It separates software generation into three user-owned layers:

1. **Typed contracts** in `codepotx.config.ts` describe resources, schemas, fields, operations, relationships, access rules, and other software intent.
2. **Template packs** combine `paths.yaml` with Handlebars files to preserve a team’s real framework, naming, folder, and code-style conventions.
3. **Consumer tasks** in `CodepotFile.yml` choose the contract and templates, control output paths, provide project variables, and run project-owned commands.

This helps AI-assisted development by making intent and implementation patterns explicit instead of forcing every agent to rediscover or guess them from the repository.

## Workspace

```text
apps/site                         Codepot website and Markdown documentation
packages/nodejs/codepotx          TypeScript authoring, templating, generation, and runtime
packages/nodejs/codepotx-cli      External codepotx CLI
packages/nodejs/codepotx-old      Archived previous TypeScript implementation
packages/python/codepotg          Deprecated Python generator reference
docs                              Shared Markdown documentation
```

## Install

```bash
corepack enable
pnpm install
```

## Common commands

```bash
pnpm typecheck
pnpm test
pnpm build
pnpm check
pnpm dev:site
```

## Three-layer example

### Typed contract

```ts
import { defineCodepotConfig, schema } from 'codepotx';

export default defineCodepotConfig({
  project: { name: 'example-platform' },
  contracts: [v1],
});
```

### Template pack

```text
templates/typescript/
├── paths.yaml
├── _partials/
└── {model}/[model.name.kebab].ts.hbs
```

### Consumer task

```yaml
allow: true

tasks:
  sdk:
    authoring: ./codepotx.config.ts
    templates: ./templates/typescript
    output: ./src/generated
    transactional: true
```

```bash
codepotx variables sdk
codepotx plan sdk
codepotx generate sdk --dry-run
codepotx generate sdk
```

## Website and documentation

The active website under `apps/site` preserves the design and component system from `archives/site` while updating the product content for the current Codepot direction.

Root `docs/*.md` files are the documentation source. `docs/navigation.json` allowlists the consumer-facing pages published through:

```text
/docs
/docs/[slug]
```

Run the site locally:

```bash
pnpm dev:site
```

## Codepot Lang

[`codepot_lang`](https://github.com/alidantech-org/codepot_lang) is the larger in-progress language direction. Its goal is to express software intent in a purpose-built strongly typed language for developers, compilers, tools, generators, and AI agents.

Use `codepotx` for the TypeScript workflow today. Codepot Lang remains experimental and does not replace it yet.

## Project rules

- Contracts, template packs, and consumer tasks remain independently reusable.
- Codepot does not hardcode a framework, ORM, language, or folder structure.
- Generation is planned and rendered before files are changed.
- Managed manifests protect user-edited and immutable files.
- No GitHub Actions workflows are used in this repository.

## License

MIT
