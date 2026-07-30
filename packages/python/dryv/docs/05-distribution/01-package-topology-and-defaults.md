# Package topology and defaults

## Runtime distribution

`dryv` contains:

- the public `DryvRuntime` facade;
- application services and the closed semantic IR;
- canonical JSON/YAML transport;
- strict project and pack configuration;
- plugin descriptors, discovery, and public ports;
- planning, rendering coordination, and diagnostics;
- memory, archive, and managed filesystem writers.

It contains no terminal package, console script, Rich/Questionary/Click dependency, or interactive behavior.

```bash
pip install dryv
```

## Command-line distribution

`dryv-cli` is the standalone terminal frontend:

```bash
pip install dryv-cli
```

It depends on `dryv` and registers:

```text
dryv
├── plan
├── generate
└── plugins
```

The CLI owns command parsing, colors, spinners, trees, prompts, machine JSON presentation, and exit codes. It contains no semantic, planning, rendering, writer, or plugin-discovery implementation.

## Authoring frontend

```bash
pip install dryv-author
```

`dryv-author` compiles typed Python declarations into an in-memory public `Contract`. It depends on the runtime's public IR and diagnostics and does not own generation.

## Optional plugins

```bash
pip install dryv-template-jinja
pip install dryv-language-typescript
pip install dryv-language-dart
```

Third-party plugins use the same public compatibility and conformance contracts.

Reusable packs remain independently versioned artifacts and are not hardcoded runtime dependencies.

## Versioning

These versions remain distinct:

- distribution release;
- Python runtime API;
- plugin API;
- IR behavior;
- project schema;
- pack schema;
- lock format;
- target/engine behavior;
- pack version.

Frontend and plugin packages declare compatible runtime ranges.

## Trust

A Python plugin is executable dependency code. A declarative pack supplies templates/data and separately approved commands. Plugin and pack trust are displayed separately.

## Fresh-install acceptance

Runtime-only environment:

```text
import dryv
from dryv import create_runtime
runtime = create_runtime()
runtime.snapshot()
runtime.plan(...)
runtime.generate(...)
runtime.generate_to_files(...)
```

CLI environment:

```text
dryv --help
dryv --version
dryv plugins
dryv plan --help
dryv generate --help
```

Acceptance requires:

- `dryv` wheel contains no `dryv/cli` package;
- `dryv` wheel declares no console script;
- `dryv-cli` wheel owns the `dryv` console script;
- `dryv-cli` imports only public runtime contracts;
- help and results contain no panel/box borders;
- machine JSON has no ANSI color;
- non-interactive execution never waits for a prompt;
- installed plugin IDs resolve once.

## Archived package isolation

The archived generator retains its original distribution and namespace. Dryv does not import or replace its internals.
