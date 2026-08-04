# Dryv runtime and orchestration plan

## Goal

Provide one reusable runtime path from a validated Dryv contract and project configuration to a complete artifact plan, deterministic memory output, and safely managed filesystem output.

The runtime is a library. CLI, IDE, server, notebook, and future interfaces consume the same public operations.

## Runtime boundary

`dryv` owns semantic contracts, validation, configuration, plugin composition, planning, rendering coordination, writers, ownership state, diagnostics, and cancellation.

`dryv-cli` owns command parsing, terminal help, colors, trees, spinners, prompts, JSON presentation, and exit codes.

## DRYV-RUNTIME-001 — Public runtime facade

**Status:** implemented initial facade; verification required

Public construction:

```python
from dryv import DryvRuntime, create_runtime

runtime = create_runtime()
explicit = DryvRuntime(plugins=plugins)
```

Implemented operations:

```python
runtime.snapshot()
runtime.plan(...)
runtime.generate(...)
runtime.generate_to_files(...)
```

The runtime owns one immutable `RuntimePlugins` graph. Plugin discovery is explicit per runtime, and tests/embedded hosts may inject the graph and writer factory.

Still planned:

- `load_project` and provider inspection;
- `validate_project`, `validate_pack`, and `validate_plugin`;
- artifact/state explanation through the facade;
- canonical transport convenience methods;
- async operation wrappers where a real host requires them.

## DRYV-RUNTIME-002 — Contract providers

**Status:** planned

Support providers returning an in-memory `Contract`:

```text
canonical IR file
Python module callable
host-supplied Contract object
```

No transport file is required when the selected provider returns a public contract.

## DRYV-RUNTIME-003 — Canonical transport

**Status:** implemented; post-rebrand verification required

- strict document/JSON/YAML encoding and decoding;
- deterministic compact JSON;
- duplicate-key-aware safe YAML;
- bounded depth and item counts;
- validation before encoding and after decoding;
- stable canonical digest.

Transport remains optional and runtime-owned.

## DRYV-RUNTIME-004 — Typed project configuration

**Status:** implemented file-source model; provider evolution planned

- exact `dryv.dev/v1` family;
- immutable project and pack models;
- safe YAML/JSON decoding;
- unknown-field rejection;
- path containment;
- typed options and bindings;
- commands preserved but fail-closed.

## DRYV-RUNTIME-005 — Pack manifest and loading

**Status:** implemented for local packs

Includes compatibility, options, bindings, selections, imports, exports, paths, symbols, deterministic discovery, symlink containment, and template/static/binary classification.

Git-backed providers remain a separate trust lane.

## DRYV-RUNTIME-006 — Plugin discovery and inspection

**Status:** implemented discovery and runtime snapshot; validation operations planned

Current entry-point groups:

```text
dryv.source_adapters
dryv.language_adapters
dryv.template_engines
```

Implemented guarantees:

- zero-argument factories;
- public protocol enforcement;
- deterministic ordering;
- duplicate ID/alias rejection;
- isolated runtime instances;
- longest suffix matching;
- safe factory-failure diagnostics;
- frontend-neutral `RuntimeSnapshot` inspection.

## DRYV-RUNTIME-007 — Fixed selectors and path expressions

**Status:** implemented current registry

Selectors remain core-owned, versioned, and introspectable. Path expressions expose only documented scalar semantic facts.

## DRYV-RUNTIME-008 — Artifact planning

**Status:** implemented first behavior version

Includes stable identities, semantic causes, target/template inference, output validation, symbols, generated dependencies, deterministic ordering, and pre-render collision diagnostics.

Planned improvements include richer ambiguity diagnostics, serializable causes, blast-radius queries, and runtime explanation methods.

## DRYV-RUNTIME-009 — Prepared render contexts

**Status:** implemented first behavior version

Contexts contain immutable semantic, project, pack, option, binding, artifact, target, import, export, and selector facts only.

## DRYV-RUNTIME-010 — Rendering

**Status:** implemented

Includes session-owned deterministic rendering, declared partials, cancellation, diagnostics, static/binary passthrough, and sorted memory output. Packs own every emitted character.

## DRYV-RUNTIME-011 — Writers and ownership state

**Status:** implemented; fault hardening planned

Memory, deterministic archive, and managed filesystem writers are available. The managed writer protects unmanaged/manual files and commits ownership state transactionally.

Still required: full commit-phase fault injection and Windows file-lock verification.

## DRYV-RUNTIME-012 — Standalone CLI

**Status:** implemented initial frontend; verification required

Distribution:

```text
packages/python/dryv-cli
```

Initial commands:

```text
dryv
├── plan
├── generate
└── plugins
```

Implementation rules now enforced by tests:

- Click owns command parsing and borderless help;
- Rich owns output, colors, trees, summaries, and spinners;
- Questionary owns interactive confirmation;
- no Python `print()` or `input()`;
- no Rich `Panel` or box-border layouts;
- JSON has no ANSI styling and never prompts;
- non-TTY generation never waits for input;
- `dryv-cli` imports only public Dryv contracts;
- the core `dryv` wheel owns no console script or terminal dependency.

Future commands are added only after matching public runtime operations exist:

```text
validate project/pack/plugin
plugins inspect
ir emit
state inspect
```

## DRYV-RUNTIME-013 — Commands and Git providers

**Status:** separate future trust lanes

Current runtime remains fail-closed for command execution and unsupported remote pack providers. Future execution requires exact arguments, provenance, approvals, restricted environment/cwd, timeouts, cancellation, and no shell interpolation.

## Verification gate

The runtime/CLI split is not complete until the exact branch head passes:

```bash
cd packages/python/dryv
python -m ruff check src tests
python -m ruff format --check src tests
python -m pytest -q
python -m build

cd ../dryv-cli
python -m ruff check src tests
python -m ruff format --check src tests
python -m pytest -q
python -m build
```

Then install both wheels in a fresh environment and verify `dryv --help`, `--version`, `plugins`, plan, memory generation, managed generation, plain JSON, prompt behavior, and console-script ownership.
