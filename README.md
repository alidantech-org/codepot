# Codepot

Codepot is a family of complementary tools for describing software intent, producing portable contracts, applying reusable template packs, and generating code safely for developers and AI agents.

The project grows through a deliberate feature-maturity path:

```text
codepot-openapi + codepotg
          ↓ prove ideas in real projects
       codepotx
          ↓ stabilize a frontend-neutral runtime
Codepot Lang + compiler/runtime + codepot CLI + LSP + extension + web + MCP
```

The current packages do not compete with or automatically replace one another. The prototype workflow remains supported while the official runtime and final language platform mature.

## Ecosystem

### Supported working prototypes

- **`codepot-openapi`** is the original TypeScript-first contract builder. It emits OpenAPI 3.1 JSON/YAML and compiler-resolved `x-codegen` metadata.
- **`codepotg`** is the stable Python and Jinja template-pack manager and generator. It consumes OpenAPI from `codepot-openapi`, infers a normalized generation model, and renders project code.

These packages are mature, continue to be worked on, and have been used in real projects.

### Official JavaScript ecosystem

- **`codepotx`** is the official stable rewrite and long-term JavaScript runtime. It owns typed authoring, templating, planning, safe generation, platform adapters, and runtime operations.
- **`codepotx-cli`** is a thin terminal frontend for `codepotx`. Domain behavior remains in the runtime so web tools, editor extensions, MCP servers, desktop applications, and embedded clients can reuse the same operations.

The JavaScript packages are under active development and are not yet presented as published stable releases.

### Final Codepot platform

[`codepot_lang`](https://github.com/alidantech-org/codepot_lang) is the Rust-based language and tooling direction. The active repository includes the strongly typed language, compiler, semantic analysis host, target-neutral IR, canonical formatter, final `codepot` CLI, LSP, and VS Code extension. Web and MCP frontends are part of the planned platform.

## Workspace

```text
apps/site                              Website and root documentation renderer
packages/nodejs/codepot-openapi        Supported TypeScript OpenAPI prototype
packages/python/codepotg               Supported Python/Jinja generator
packages/nodejs/codepotx               Official JavaScript runtime rewrite
packages/nodejs/codepotx-cli           Thin CLI frontend for codepotx
docs                                   Public documentation source
```

## Documentation

All public site documentation is authored under root [`docs/`](./docs). The site reads `docs/navigation.json`, loads the listed Markdown sources, and renders them under `/docs`.

The central [`docs/ecosystem.json`](./docs/ecosystem.json) file records product status, documentation routes, install commands, source links, package registries, and reserved links for future releases.

Run the site locally:

```bash
corepack enable
pnpm install
pnpm --filter @codepot/site dev
```

Validate and build the documentation site:

```bash
pnpm --filter @codepot/site validate:docs
pnpm --filter @codepot/site build
```

## Workspace commands

```bash
pnpm typecheck
pnpm test
pnpm build
pnpm check
```

## Project principles

- Software meaning and generated implementation patterns remain explicit and reviewable.
- Contracts, template packs, generation tasks, runtimes, and frontends keep clear ownership boundaries.
- Frameworks, ORMs, target languages, and folder structures are not hardcoded into the project identity.
- Planning and validation happen before filesystem mutation.
- Supported prototypes remain useful while validated behavior moves into stable rewrites.
- The final Codepot platform gives developers, tools, and AI agents the same typed semantic foundation.
- No GitHub Actions workflows are used in this repository.

## License

MIT
