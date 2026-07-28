# Dryv

Dryv is the reusable software-derivation runtime in the Codepot ecosystem.

> Define once. Derive everywhere.

The `dryv` distribution owns semantic contracts, validation, planning, plugin composition, deterministic rendering, and managed output. It intentionally contains no terminal frontend, prompts, colors, command parser, or console script.

## Runtime-first API

```python
from dryv import create_runtime

runtime = create_runtime()

snapshot = runtime.snapshot()
plan_result = runtime.plan("dryv.yaml")
memory_result = runtime.generate("dryv.yaml")
file_result, write_report = runtime.generate_to_files(
    "dryv.yaml",
    destination="generated",
)
```

A runtime instance owns one plugin graph and can be reused by a CLI, IDE, server, notebook, MCP adapter, test, or application host.

For explicit dependency injection:

```python
from dryv import DryvRuntime, RuntimePlugins

runtime = DryvRuntime(
    plugins=RuntimePlugins(
        source_adapters=(source_adapter,),
        target_adapters=(target_adapter,),
        template_engines=(template_engine,),
    )
)
```

No process-global runtime or mutable plugin registry is required.

## Runtime responsibilities

```text
DryvRuntime
├── snapshot            inspect loaded runtime capabilities
├── plan                validate and build the complete artifact plan
├── generate            render deterministic in-memory output
└── generate_to_files   commit output through a managed writer
```

The runtime owns:

- the closed immutable semantic IR;
- canonical validation and diagnostics;
- project and pack configuration;
- source, target, and template-engine plugin composition;
- fixed semantic selection and artifact planning;
- immutable template contexts;
- deterministic memory generation;
- transactional managed filesystem output;
- manual-edit and unmanaged-collision protection;
- optional canonical JSON/YAML transport.

## Package family

```text
dryv
├── dryv-author
├── dryv-cli
├── dryv-template-jinja
├── dryv-language-typescript
└── dryv-language-dart
```

Dependency direction:

```text
dryv-cli ----------------------> dryv
dryv-author -------------------> dryv
dryv-template-jinja -----------> dryv
dryv-language-typescript ------> dryv
dryv-language-dart ------------> dryv
```

The runtime does not depend on any frontend or optional plugin package.

## Terminal frontend

Install `dryv-cli` for the command-line interface:

```bash
python -m pip install dryv-cli
```

The CLI consumes only the public runtime API and owns all command parsing, Rich output, Questionary prompts, spinners, trees, JSON presentation, and exit-code behavior.

```text
dryv
├── plan
├── generate
└── plugins
```

## Project and pack contracts

Dryv uses two authored configuration files:

```text
dryv.yaml       project-owned orchestration
DryvPack.yaml   pack-owned generation behavior
```

A project selects semantic inputs, pack instances, outputs, options, and bindings. A pack owns templates, static files, selections, paths, symbols, dependencies, options, bindings, and compatibility requirements.

## Plugins

The current runtime discovers:

```text
dryv.source_adapters
dryv.language_adapters
dryv.template_engines
```

The built-in `ir` source adapter loads canonical Dryv contracts. TypeScript and Dart target facts and the Jinja engine remain independently installable.

## Managed generation

Dryv plans the complete artifact set before writing. The managed writer:

- rejects unmanaged collisions;
- refuses to overwrite manually edited managed files;
- removes only unchanged stale managed files;
- updates state only after a successful commit;
- rolls back failed commits.

Ownership metadata is stored under:

```text
.dryv/generation-state.json
```

## Verification

From `packages/python/dryv`:

```bash
python -m pip install -e ".[dev]"
python -m ruff check src tests
python -m ruff format --check src tests
python -m pytest -q
python -m build
```

The connected manual project is under `examples/manual/connected-project`.

## Design principles

- One closed, typed, versioned semantic authority.
- One reusable runtime API for every frontend.
- Templates own every emitted character.
- Target plugins provide validation and path/module facts, never syntax rendering.
- Planning completes before rendering or writing.
- Full generation remains the correctness reference for incremental work.
- Reproducibility and safe failure take priority over shortcuts.

Start with [`docs/README.md`](docs/README.md) for the architecture, configuration, generation, plugin, and distribution guides.
