# Shipping rules

These rules apply to the final hardening program.

## Template contracts

- Every value exposed to templates must exist in a versioned, serializable variable catalog.
- Handlebars variable, helper, partial, block-parameter, and `@data` references must be collected without executing templates.
- `paths.yaml` selectors and output expressions are validated against the same catalog used for template validation.
- A template pack may declare stricter required variables, but it cannot invent undeclared runtime values.
- Catalog output must be available through the runtime, CLI, JSON, and documentation.

## Generation safety

- Complete rendering happens in memory before writing or deleting files.
- Duplicate output paths are errors unless an explicit deterministic merge strategy exists.
- Cleanup defaults to files recorded in a Codepot-managed manifest; broad clean roots require explicit configuration.
- Immutable files are never overwritten or deleted by normal generation.
- Transactional tasks stage changes and restore previous managed files when required writes or commands fail.
- Required command failures stop the task; optional command failures are reported without hiding their exit status.
- Plans, manifests, reports, and generated content must be deterministic for deterministic inputs.

## Dependency and import planning

- Dependencies are semantic facts with a purpose and target reference.
- Output paths are indexed before rendering.
- Language-specific import statements are produced by injected adapters, not hardcoded in core generation.
- Missing dependency targets, ambiguous targets, and self-imports receive explicit diagnostics.

## Documentation and site

- Root `docs/` is the source of truth for authored documentation.
- The site reads root docs and generated reference data; it does not maintain a second hidden copy.
- Examples are executable or statically validated.
- The archived site design is preserved where useful, but all Codepurify and OpenAPI-first product wording is removed.
- Docker standalone deployment is the provider-neutral baseline. GitHub Actions remain prohibited.

## Reviewability

- Public classes, ports, artifacts, and non-obvious algorithms require comments explaining intent, invariants, and failure behavior.
- Comments explain why; they do not repeat obvious syntax.
- Large modules are split by responsibility and keep types separate from implementation.
