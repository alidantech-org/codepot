# Dryv

Dryv is the reproducible software derivation runtime in the Codepot ecosystem.

It coordinates a closed semantic contract, reusable packs, language adapters, template engines, planning, deterministic rendering, and managed output. The same semantic meaning can drive several target implementations without placing target syntax inside the semantic kernel.

> Define once. Derive everywhere.

## Package responsibility

The `dryv` distribution is the runtime and orchestration library. It owns:

- the canonical immutable IR;
- semantic validation and diagnostics;
- project and pack configuration contracts;
- plugin discovery and compatibility checks;
- selection and artifact planning;
- template-context preparation;
- deterministic in-memory generation;
- transactional managed output;
- generation ownership state and manual-edit protection;
- optional canonical JSON and YAML transport.

The runtime must remain independent of terminal formatting and interactive interfaces. Command-line behavior is moving to the separate `dryv-cli` distribution.

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

The runtime does not depend on the CLI, authoring frontend, template engine, or language packages.

## Runtime flow

```text
Python authoring or canonical IR
              ↓
       immutable Contract
              ↓
          Dryv runtime
              ├── loads dryv.yaml
              ├── resolves packs
              ├── discovers plugins
              ├── validates the complete plan
              ├── renders through template engines
              └── commits managed output safely
```

JSON and YAML are optional transport and inspection formats. They are not required intermediate files when a host provides an in-memory contract.

## Public namespaces

```python
from dryv import generate, generate_to_files
from dryv.diagnostics import Diagnostic, Diagnostics
from dryv.ir import Contract, Group, Operation, Schema
from dryv.ports import TargetAdapter, TemplateEngine
from dryv.runtime import RuntimePlugins
```

The public `dryv.ir` and `dryv.generation` packages are stable facades over internal domain implementations. Plugins must depend only on published Dryv namespaces.

## Project and pack contracts

Dryv uses two authored configuration files:

```text
dryv.yaml       project-owned orchestration
DryvPack.yaml   pack-owned generation behavior
```

A project selects semantic input, pack instances, outputs, options, and bindings. A pack owns its templates, static files, selections, output patterns, options, bindings, and compatibility requirements.

## Plugin families

The current runtime discovers:

```text
dryv.source_adapters
dryv.language_adapters
dryv.template_engines
```

The built-in `ir` source adapter loads canonical Dryv contracts. TypeScript and Dart language facts and the Jinja template engine remain separately installable plugins.

## Managed generation

Dryv plans the complete artifact set before writing files. The managed writer:

- rejects unmanaged path collisions;
- refuses to overwrite manually changed managed files;
- removes only unchanged stale managed files;
- updates ownership state only after a successful commit;
- leaves the destination unchanged when generation fails.

Ownership metadata is stored under:

```text
.dryv/generation-state.json
```

## Local verification

From `packages/python/dryv`:

```bash
python -m pip install -e ".[dev]"
python -m ruff check src tests
python -m ruff format --check src tests
python -m pytest -q
python -m build
```

The connected manual project is under:

```text
examples/manual/connected-project
```

It validates direct canonical IR, typed Python authoring, local TypeScript and Dart packs, Jinja rendering, compiler checks, deterministic regeneration, and managed-output protection.

## Design principles

- One closed, typed, versioned semantic authority.
- Templates own every emitted character.
- Language plugins provide validation and path/module facts, not syntax rendering.
- Planning completes before rendering or writing.
- Full generation remains the correctness reference for incremental work.
- Packs and plugins are ordinary versioned Python distributions.
- Runtime services are reusable from CLI, IDE, server, notebook, and test hosts.
- Reproducibility and safe failure take priority over convenience shortcuts.

## Documentation

Start with [`docs/README.md`](docs/README.md), then read the architecture, configuration, generation, plugin, and distribution sections. A practical Dryv Cookbook will become the primary task-oriented guide as the package split stabilizes.
