# codepotg-language-typescript

Installable TypeScript target detection, validation, and module-path adapter for CodepotG v2.

The adapter is resolved per template from target suffixes such as `.ts`, `.tsx`, `.mts`, and `.cts`.

It does **not** own TypeScript code generation. Template packs, macros, partials, and static files author every TypeScript character, including types, literals, comments, imports, exports, decorators, validators, and framework code.

## Planned entry point

```toml
[project.entry-points."codepotg.language_adapters"]
typescript = "codepotg_language_typescript.plugin:create_plugin"
```

## Responsibilities

- TypeScript target suffix detection, including longest-known names such as `.d.ts` outputs;
- output filename, reserved-name, and declared candidate-identifier validation;
- relative, alias, package/module, project-path, barrel, index, and extension module-specifier facts;
- deterministic target/path capability descriptors and typed validation options;
- diagnostics, introspection, compatibility, and conformance behavior.

## Prohibited responsibilities

- semantic-kernel/facet/selector extension;
- type, literal, comment, import, export, decorator, validator, or framework rendering;
- template selection, output planning, filesystem writes, commands, OpenAPI, Node/NestJS/Next.js/React policy.

See [`docs/design/README.md`](docs/design/README.md) and [`docs/tasks/00-package-plan.md`](docs/tasks/00-package-plan.md).
