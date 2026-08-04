# Dryv Jinja template engine

`dryv-template-jinja` is an optional template-engine adapter. It renders only through runtime-provided immutable contexts and must preserve sandbox, bounded-resource, determinism, and template-owned-syntax rules.

- [`engine-contract.md`](engine-contract.md) — adapter and security contract.
- [`design/`](design/README.md) — package design.
- [`benchmarks.md`](benchmarks.md) — isolated v1/v2 benchmark workflow using `uv` without environment activation.
- [`../../../tasks/dryv/template-jinja`](../../../tasks/dryv/template-jinja/README.md) — task ledger.
