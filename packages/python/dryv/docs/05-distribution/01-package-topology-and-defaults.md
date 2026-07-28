# Package topology and bundled defaults

## Minimal core

`dryv` contains:

- public Python API and application services;
- neutral IR and generation domain;
- typed configuration and rule protocols;
- plugin descriptors/registries/ports;
- runtime/session composition;
- standard diagnostics/events/results;
- default memory/filesystem/archive infrastructure where approved.

It does not require OpenAPI, TypeScript, Dart, Jinja, or official packs.

## Batteries-included distribution

The normal user installs:

```bash
pip install dryv
```

The `dryv` distribution depends on compatible releases of:

```text
dryv
dryv-openapi
dryv-language-typescript
dryv-language-dart
dryv-template-jinja
dryv-pack-typescript-sdk
dryv-pack-dart-sdk
dryv-pack-flutter-sdk
```

This package may be a small dependency bundle plus CLI entry point. Defaults are still discovered through public entry points; core has no hardcoded TypeScript/Dart/Jinja branches.

## Optional extensions

Additional language, engine, source, ecosystem, or pack packages install normally or through extras where useful:

```bash
pip install "dryv[kotlin]"
pip install acme-dryv-language-csharp
```

Third-party plugins use the same compatibility and conformance rules as official packages.

## Versioning

The following versions are distinct:

- package release;
- Python public API;
- plugin API;
- IR;
- project schema;
- pack schema;
- lock file;
- language/engine behavior;
- pack version.

The batteries-included distribution pins compatible ranges so a simple installation cannot combine known-incompatible contracts.

## Trust

Installing a Python plugin grants executable Python dependency trust. Installing a declarative pack supplies data/templates plus separately approved commands. Plugin and pack trust must be displayed distinctly.

## Fresh-install acceptance

A clean installation must support:

```text
import dryv
dryv plugins
dryv validate
dryv configure
dryv generate
```

The plugin list should immediately show the bundled OpenAPI, TypeScript, Dart, Jinja, and official pack capabilities.

## Development cutover

The new distribution is built/tested in isolated environments while the old package remains in the repository. The final release replaces the old published runtime; the two distributions are not expected to be installed side by side while both own the `dryv` import namespace.
