# TypeScript SDK pack design reference

## Purpose

This pack generates framework-neutral TypeScript SDK artifacts from neutral IR. It is authored entirely through `CodepotgPack.yaml`, templates, partials, static files, bindings, dependencies, setup, and documented profiles.

## Planned profiles

- `modular` — separate models, DTOs, operations/client, errors, and authored barrels;
- `minimal` — core types/client only;
- `monolithic` — one aggregate TypeScript file;
- optional `standalonePackage` — owns package metadata and package folder;
- optional `contribute` — adds generated files/dependency intent to an existing project.

Profiles select declared files; they never select a global language.

## File examples

```text
templates/
├── models/model.ts.jinja
├── models/enum.ts.jinja
├── operations/operation.ts.jinja
├── client.ts.jinja
├── index.ts.jinja
├── all.ts.jinja
├── README.md.jinja
├── package.json.jinja
├── .gitignore
└── _partials/license.txt.jinja
```

`index.ts.jinja` is an authored barrel. `.gitignore` is copied as static content. `all.ts.jinja` receives aggregate selections for single-file output.

## Project configuration example

```yaml
packs:
  sdk:
    use:
      github: alidantech-org/codepotg-typescript-sdk-pack
      ref: v2.0.0
    source: backendApi
    profile: modular
    output:
      root: packages/api-sdk
    options:
      generateExamples: true
    bindings:
      common:
        from:
          barrel: "@modules/common"
        symbols:
          logger: AppLogger
          authToken: TokenProvider
    overrides:
      languages:
        typescript:
          imports:
            aliases:
              "@": ./src
```

The project user does not list internal templates.

## Pack responsibilities

- deterministic selections and grouping;
- file discovery and output expressions;
- authored templates/partials/static files;
- public options and bindings;
- TypeScript and Jinja pack defaults;
- Node dependency/manifest intent;
- configure prompts and manual steps;
- approved optional lint/format/typecheck actions.

## Boundaries

The pack does not implement TypeScript syntax itself, run commands from templates, parse OpenAPI, write files, or use old `paths.yaml` behavior.

See `../tasks/00-package-plan.md` for the exact implementation ledger.
