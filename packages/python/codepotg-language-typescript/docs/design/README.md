# TypeScript adapter design reference

## Role

This package is resolved independently for every template whose target is TypeScript. It implements target syntax and typed TypeScript rules; it never selects templates or assumes a framework.

## Planned plugin entry point

```toml
[project.entry-points."codepotg.language_adapters"]
typescript = "codepotg_language_typescript.plugin:create_plugin"
```

## Target descriptors

```text
typescript: .ts, .mts, .cts
typescript-jsx: .tsx
```

The exact descriptor split is an implementation decision, but all targets use one package and share compatible rules. Longest-known suffix matching preserves names such as `types.d.ts.jinja` as `types.d.ts` output.

## Pack rules example

```yaml
languages:
  typescript:
    identifiers:
      reservedWordPolicy: suffix
      suffix: _
    naming:
      types: pascalCase
      values: camelCase
      files: kebabCase
    modules:
      syntax: esm
    imports:
      strategy: relative
      aliases: {}
      omitExtensions: true
      indexResolution: omitIndex
      typeImports: separate
      quoteStyle: double
      ordering: [sideEffect, external, alias, relative]
    exports:
      typeExports: separate
    types:
      optionalProperties: questionMark
      nullable: unionNull
      date: string
      binary: Uint8Array
    literals:
      quoteStyle: double
    comments:
      documentation: jsdoc
```

Every field is implemented by a typed dataclass/value object and a separate typed patch. The final field names may be refined before stable release, but no raw dictionary reaches the adapter.

## Project override example

```yaml
packs:
  sdk:
    overrides:
      languages:
        typescript:
          imports:
            strategy: alias
            aliases:
              "@": ./src
```

The pack may restrict which fields can be overridden.

## Semantic import example

A template requests logical symbols. The adapter receives the planned output path and binding/provider descriptors, then produces imports such as:

```typescript
import type { User } from "@/models/user";
import { BaseRepository, AppLogger } from "@modules/common";
```

The template does not calculate `../` paths or manually deduplicate barrel symbols.

## Internal implementation shape

```text
TypeScriptLanguageAdapter
├── IdentifierPolicy
├── NamingPolicy
├── TypeRenderer
├── LiteralRenderer
├── CommentRenderer
├── ModulePathResolver
├── ImportPlanner
└── ExportPlanner
```

Each component is independently unit tested. The facade implements the public language adapter protocol.

## Boundaries

This package contains no:

- OpenAPI parsing;
- Node package-manager or `package.json` modification;
- NestJS/Next.js/React rules;
- Jinja rendering;
- template selection;
- output writing;
- command execution;
- old generator imports.

See the detailed task ledger in `../tasks/00-package-plan.md` and the core contract in `codepotg-v2/docs/04-plugins/02-language-adapter-contract.md`.
