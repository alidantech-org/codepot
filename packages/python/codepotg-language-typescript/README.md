# codepotg-language-typescript

Installable TypeScript target-language adapter for CodepotG v2.

The adapter is resolved per template from target suffixes such as `.ts`, `.tsx`, `.mts`, and `.cts`. It owns TypeScript syntax and typed language rules, not OpenAPI, Node.js, NestJS, Next.js, React, template selection, output planning, or filesystem writes.

## Planned entry point

```toml
[project.entry-points."codepotg.language_adapters"]
typescript = "codepotg_language_typescript.plugin:create_plugin"
```

## Responsibilities

- identifiers and reserved words;
- type, literal, comment, import, export, and module-path rendering;
- relative, alias, package, namespace, barrel, and project-path import policies;
- typed rule defaults, patches, merge semantics, override limits, and validation;
- deterministic conformance behavior for all TypeScript-targeting templates.

See [`docs/tasks/00-package-plan.md`](docs/tasks/00-package-plan.md).
