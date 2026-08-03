# Codepot engineering rules

## Contract-first implementation

- Define interfaces, ports, method signatures, request/result types, errors, and events before concrete classes or functions.
- A concrete class implements a named interface or is returned behind a named port.
- Public and cross-module methods must have explicit input and output contracts before implementation begins.
- Keep declarations separate from runtime code:
  - `*.types.ts` — interfaces, type aliases, generics, and type-only declarations;
  - `*.contracts.ts` — ports, requests, results, artifacts, and method contracts;
  - `*.constants.ts` — runtime constants;
  - `*.schema.ts` — runtime validation schemas;
  - normal `*.ts` files — implementations.
- Tiny private implementation-only types may remain beside their implementation when they are not part of a module boundary.

## Dependency inversion

- High-level modules depend on contract ports, never concrete platform adapters.
- Runtime creates and injects implementations.
- No global singleton container, implicit service lookup, or mutable shared compiler state.
- No cross-layer implementation imports.
- Events cannot replace required typed calls or returned values.

## Module boundaries

- `contract` contains no Zod, Handlebars, YAML, Node filesystem, Git, shell, cache, or CLI dependencies.
- `platform` implements infrastructure ports and contains shared I/O behavior.
- `authoring` owns user-facing DSL, config loading, compatibility, validation, and canonical compilation.
- `templating` owns `paths.yaml`, Handlebars, template contexts, dependency/import planning, and rendering.
- `generation` owns `CodepotFile.yml`, task orchestration, planning, lifecycle enforcement, writing, cleanup, and commands.
- `runtime` owns composition, run context, service wiring, request dispatch, cancellation, and events.
- `codepotx-cli` owns argument parsing, prompts, terminal presentation, and exit codes only.

## Compatibility

- Port old authoring behavior mechanically before redesigning it.
- Preserve runtime exports, type exports, builder methods, generic inference, refs, metadata, errors, validation, and semantic output.
- Existing contracts should normally change only imports.
- Export `z` from `codepotx` for compatibility and `schema` as the preferred curated namespace.
- Zod remains an internal dependency and must not become a peer dependency or leak into stable artifacts.
- `package.config.ts` and `definePackageConfig` may be accepted temporarily through a compatibility adapter, while new documentation uses `codepotx.config.ts` and `defineCodepotConfig`.

## Stable artifacts

- Stable artifacts are deterministic, immutable, serializable, and explicitly versioned.
- They contain no functions, class instances, mutable registries, Zod schemas, Handlebars templates, CLI output state, or unresolved machine-local objects.
- Preserve source references and diagnostics in a portable form.
- Add protocol migrations deliberately; never silently change artifact meaning.

## Shared infrastructure

- Do not create a generic `utils/` dumping ground.
- Shared reusable I/O belongs behind focused ports in `contract` and implementations in `platform`.
- Reuse one YAML/JSON codec, source resolver, module loader, filesystem abstraction, hasher, cache, command runner, and changed-aware writer.
- Domain validation stays inside its owning module even when file reading/parsing is shared.

## Files and imports

- Use extensionless TypeScript imports.
- Use `@/*` only for internal package source imports; bundling must remove aliases from published output.
- Prefer focused module entrypoints over deep public imports.
- Avoid broad barrel files that create circular dependencies.
- Use POSIX-style stable relative paths inside serialized artifacts where possible.

## Events and diagnostics

- Events are typed, versioned, ordered, correlated to a run, and observer-only.
- Listener failures must not alter domain results.
- Errors use structured diagnostics with code, severity, message, source, location, hints, and related diagnostics where applicable.
- Do not log directly from domain code; publish diagnostics/events through injected ports.

## Testing

- Prefer in-memory platform adapters for unit tests.
- Add compatibility fixtures from real old contracts before porting authoring modules.
- Compare canonical artifacts, template contexts, plans, generated files, write decisions, and diagnostics.
- Validate package exports with Publint and Are The Types Wrong before release.
