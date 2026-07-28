# Package topology and defaults

## Runtime distribution

`dryv` contains:

- public runtime and application services;
- canonical immutable IR and transport;
- typed project and pack configuration;
- plugin descriptors, registries, and ports;
- planning and rendering coordination;
- diagnostics, cancellation, events, and structured results;
- memory, archive, and managed filesystem writers.

It does not require the CLI, Python authoring frontend, TypeScript plugin, Dart plugin, Jinja plugin, or any reusable pack.

Install only the runtime:

```bash
pip install dryv
```

## Command-line distribution

`dryv-cli` is a standalone interface package:

```bash
pip install dryv-cli
```

It depends on `dryv` and registers the `dryv` command. It must contain no planning, generation, plugin, pack, transport, or writer implementation.

## Authoring frontend

```bash
pip install dryv-author
```

`dryv-author` depends on the runtime's public IR and diagnostics. It compiles typed Python declarations into an in-memory `Contract` and does not own generation or canonical transport.

## Optional plugins

```bash
pip install dryv-template-jinja
pip install dryv-language-typescript
pip install dryv-language-dart
```

Additional language, engine, provider, ecosystem, or infrastructure plugins install as normal Python distributions:

```bash
pip install acme-dryv-language-csharp
```

Third-party plugins use the same compatibility and conformance rules as official packages.

Reusable packs are versioned artifacts and may be distributed through Git, package archives, Python distributions, or a future marketplace without being hardcoded into the runtime.

## Versioning

The following versions are distinct:

- distribution release;
- Python public API;
- plugin API;
- IR behavior;
- project schema;
- pack schema;
- lock file;
- target/engine behavior;
- pack version.

Interface and plugin packages declare compatible runtime ranges so an installation cannot combine known-incompatible public contracts.

## Trust

Installing a Python plugin grants executable Python dependency trust. Installing a declarative pack supplies templates and data plus separately approved commands. Plugin and pack trust must be displayed distinctly.

## Fresh-install acceptance

Runtime-only environment:

```text
import dryv
canonical IR encode/decode
runtime validation and planning APIs
memory/archive/managed writer APIs
```

Full development environment:

```text
import dryv
import dryv_author
IR, TypeScript, Dart, and Jinja plugin entry points resolve exactly once
dryv validate project
dryv validate pack
dryv validate plugin
dryv plan
dryv generate
```

The command checks require `dryv-cli`; runtime imports and operations do not.

## Archived package isolation

The archived generator keeps its original distribution and import namespace. Dryv uses distinct package names and is tested in isolated environments so the two product lines do not shadow one another.
