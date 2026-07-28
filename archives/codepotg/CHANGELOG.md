# Changelog

## 1.0.0 — First stable PyPI release

- Publishes the established Python and Jinja OpenAPI generator as `codepotg`.
- Supports OpenAPI 3.0 and 3.1 JSON or YAML input.
- Uses the Python-specific `Codepotg.yaml` task file and rejects the TypeScript workflow's `CodepotFile.yml` and `CodepotFile.yaml` names.
- Uses bundled language templates when `templateDir` is omitted.
- Includes TypeScript, Next.js, Dart, and debug template packs.
- Preserves inference, dependency/import planning, frontend metadata, `x-codegen` metadata, managed writes, immutable scaffolds, guarded cleanup, dry runs, commands, and diagnostics.
- Adds an installed-wheel-safe `codepotg` console entry point.
- Adds `codepotg --version` and `python -m codepotg`.
- Establishes OpenAPI 3.0.3 and 3.1.0 as the initial compatibility baseline for the wider Codepot ecosystem.
- Adds guarded release tooling that validates metadata, wheel contents, source-distribution contents, clean installation, and CLI startup before upload.

The Python package remains supported for OpenAPI-driven generation. Today, `codepot-openapi` is the supported TypeScript producer for enriched Codepot OpenAPI documents. Future `codepotx` OpenAPI compatibility can be adopted after its output is implemented and validated against the stable package.
