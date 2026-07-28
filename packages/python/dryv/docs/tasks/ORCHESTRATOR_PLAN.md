# Dryv runtime and orchestration plan

## Goal

Provide one reusable runtime path from a validated Dryv contract and typed project configuration to a complete artifact plan, deterministic memory output, and safely managed filesystem output.

The runtime is a library. CLI, IDE, server, notebook, and future user interfaces call the same public operations.

## Runtime boundary

`dryv` owns:

- canonical IR and transport;
- project and pack configuration;
- plugin discovery and validation;
- pack loading and compatibility;
- selection and artifact planning;
- prepared render contexts;
- template-engine coordination;
- target-adapter coordination;
- deterministic memory output;
- archive and managed filesystem writers;
- ownership state and manual-edit protection;
- structured diagnostics and cancellation.

`dryv` does not own terminal parsing, terminal formatting, prompts, or interactive flows.

## DRYV-RUNTIME-001 — Public runtime facade

**Status:** planned

Create:

```python
from dryv import DryvRuntime

runtime = DryvRuntime.discover()
```

Initial operations:

```python
runtime.load_project(...)
runtime.load_contract(...)
runtime.validate_project(...)
runtime.validate_pack(...)
runtime.validate_plugin(...)
runtime.plugins()
runtime.plan(...)
runtime.generate(...)
runtime.generate_to_files(...)
runtime.emit_contract(...)
runtime.inspect_state(...)
```

Every operation returns structured results and diagnostics.

## DRYV-RUNTIME-002 — Contract providers

**Status:** planned

Support contract providers that return an in-memory `Contract`:

```text
canonical IR file
Python module callable
host-supplied Contract object
```

The Python provider imports a configured module and callable in an isolated, explicit operation. It validates that the result is a public Dryv contract and reports import/call failures safely.

No transport file is required when the provider returns an in-memory contract.

## DRYV-RUNTIME-003 — Canonical transport

**Status:** implemented; cleanup required

- strict document/JSON/YAML encoding and decoding;
- explicit format, IR, and behavior versions;
- deterministic compact JSON;
- safe duplicate-key-aware YAML;
- bounded depth and item counts;
- validation before encoding and after decoding;
- stable canonical digest.

Transport remains optional and runtime-owned.

## DRYV-RUNTIME-004 — Typed project configuration

**Status:** implemented; evolve to provider model

- exact `dryv.dev/v1` API family;
- immutable project and pack-instance models;
- safe YAML/JSON decoding;
- unknown-field rejection;
- path containment;
- typed options and bindings;
- commands preserved but fail-closed until an approved command runtime exists.

Update the current source model so a project can select a contract provider instead of requiring every source to be a file adapter.

## DRYV-RUNTIME-005 — Pack manifest and loading

**Status:** implemented for local packs

- `DryvPack.yaml` decoding;
- metadata and compatibility;
- include/exclude rules;
- options, bindings, selections, imports, exports, paths, and symbols;
- deterministic discovery;
- mandatory template root;
- symlink and path containment;
- template, partial, static, and binary classification.

Git-backed pack providers remain a separate trust and distribution lane.

## DRYV-RUNTIME-006 — Plugin discovery

**Status:** implemented; validation commands planned

Current groups:

```text
dryv.source_adapters
dryv.language_adapters
dryv.template_engines
```

Required guarantees:

- zero-argument factories;
- public protocol enforcement;
- deterministic ordering;
- duplicate ID and alias rejection;
- isolated runtime instances;
- longest suffix matching;
- safe factory-failure diagnostics.

Add public plugin-validation and inspection operations before expanding plugin categories.

## DRYV-RUNTIME-007 — Fixed selectors and path expressions

**Status:** implemented current registry

Selectors remain core-owned, versioned, and introspectable. Packs cannot register arbitrary traversal queries.

Path expressions allow only documented roots, scalar properties, naming projections, and literal segments. Calls, private attributes, runtime objects, and arbitrary graph traversal remain forbidden.

## DRYV-RUNTIME-008 — Artifact planning

**Status:** implemented first behavior version

- stable artifact identity separate from destination;
- semantic, group, selection, template, and pack cause tracking;
- target and template suffix handling;
- output-path validation;
- symbol evaluation;
- generated dependency resolution;
- deterministic plan ordering;
- collision diagnostics before rendering.

Planned improvements:

- richer provider ambiguity diagnostics;
- serializable cause graph;
- semantic blast-radius queries;
- plan explanation through the runtime facade.

## DRYV-RUNTIME-009 — Prepared render contexts

**Status:** implemented first behavior version

Contexts contain immutable safe facts only:

```text
project
pack
options
bindings
artifact
target
imports
exports
contract
selector-specific semantic roots
```

No filesystem handles, secrets, mutable registries, runtime services, authoring builders, Pydantic classes, or arbitrary callables enter templates.

## DRYV-RUNTIME-010 — Rendering

**Status:** implemented

- deterministic session-owned rendering;
- strict UTF-8 template sources;
- declared in-memory partials;
- sandboxed engine calls;
- cancellation and structured diagnostics;
- static and binary passthrough;
- sorted `MemoryOutput`.

Templates, macros, partials, and static files own every emitted character.

## DRYV-RUNTIME-011 — Writers and ownership state

**Status:** implemented; fault hardening planned

Memory writer:

- primary generated result;
- deterministic artifact order and bytes.

Archive writer:

- sorted entries;
- fixed metadata;
- atomic replacement.

Managed filesystem writer:

- `.dryv/generation-state.json`;
- create/change/leave/delete/protect reporting;
- unmanaged collision refusal;
- manual-edit protection;
- unchanged stale-file deletion;
- staged transactional commit;
- rollback on failure.

Add fault injection for every commit phase and verify Windows file-lock behavior.

## DRYV-RUNTIME-012 — CLI extraction

**Status:** planned

Move command parsing and JSON terminal output into `dryv-cli`.

Initial commands:

```text
dryv plan
dryv generate
dryv validate project
dryv validate pack
dryv validate plugin
dryv plugins list
dryv plugins inspect
dryv ir emit
dryv state inspect
```

The CLI contains no planning, rendering, plugin, pack, or writer logic.

## DRYV-RUNTIME-013 — Commands and Git providers

**Status:** separate future trust lanes

Current runtime remains fail-closed for unapproved command execution and unsupported remote pack providers.

Any future command runtime requires exact arguments, provenance, approvals, environment restrictions, timeouts, cancellation, contained working directories, and no shell interpolation.

Any future Git provider requires generic Git support, immutable resolved commits, safe contained snapshots, credential separation, integrity verification, offline reuse, and `dryv.lock.yaml`.

## DRYV-RUNTIME-014 — Explain, impact, and incremental generation

**Status:** artifact explanation partially implemented

Required before incremental generation:

- semantic-to-selection edges;
- selection-to-artifact edges;
- generated provider edges;
- template and partial edges;
- configuration and pack causes;
- serializable impact results;
- proof that incremental output equals a fresh full generation byte-for-byte.

Full deterministic generation remains the correctness reference.

## DRYV-RUNTIME-015 — Verification and release

Run all package suites after the rebrand and CLI extraction:

```bash
python -m ruff check src tests
python -m ruff format --check src tests
python -m pytest -q
python -m build
```

Then verify real wheels together in a fresh environment:

- plugin entry points resolve exactly once;
- direct IR and Python authoring routes plan and generate;
- generated TypeScript compiles;
- generated Dart analyzes;
- deterministic reruns leave managed files unchanged;
- edited managed and unmanaged files are protected;
- stale unchanged managed files are removed safely;
- old names and retired source references are absent;
- the final working tree is clean.
