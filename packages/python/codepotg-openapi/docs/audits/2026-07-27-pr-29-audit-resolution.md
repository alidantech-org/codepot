# PR #29 critical audit repair resolution

**Date:** 2026-07-27  
**Base:** `chatgpt/codepotx-restart`  
**Repair branch:** `chatgpt/codepotx-restart-openapi-audit-fixes`  
**Original audit:** [`2026-07-27-pr-29-audit.md`](2026-07-27-pr-29-audit.md)

## Resolution verdict

The critical implementation blockers identified after PR #29 have been repaired in code and covered by repository tests. The package now has a real public source-adapter facade for the implemented standard OpenAPI subset.

The lane remains **review**, not **complete**, until the synchronized repository checkout runs the complete Ruff, pytest, build, wheel/sdist, and isolated-install command set. This execution environment cannot resolve GitHub or package-index DNS, so it does not claim those commands passed.

## Resolved critical findings

### OPENAPI-AUDIT-001 — missing adapter module

Resolved:

- added `src/codepotg_openapi/adapter.py`;
- `create_plugin()` returns `OpenApiSourceAdapter`;
- `from codepotg_openapi import OpenApiSourceAdapter` resolves;
- the registered `codepotg.source_adapters/openapi` factory has direct and isolated-wheel tests.

### OPENAPI-AUDIT-002 — no composed normalization path

Resolved with one public pipeline per `normalize()` call:

```text
options
→ fresh loading session
→ controlled root load
→ bounded JSON/YAML parse and structure validation
→ session reference preflight/resolution
→ standard groups/schemas/operations normalization
→ immutable Contract
→ codepotg.ir.validate_contract
→ deterministic digest
→ SourceAdapterResult
```

Adapter errors and cancellation return diagnostics rather than leaking implementation exceptions.

### OPENAPI-AUDIT-003 — unsupported README claims

Resolved:

- removed the typed `x-codegen` capability claim;
- rewrote `README.md` around implemented standard OpenAPI behavior;
- added `docs/support/README.md`;
- removed nonexistent benchmark-document claims;
- explicitly lists OA-009..OA-015/OA-019/OA-020 as unimplemented.

Typed `x-codegen` now emits `OA_XCODEGEN_NOT_IMPLEMENTED`: tolerant policy warns and ignores it; strict/deny return no contract.

OpenAPI security declarations emit `OA_SECURITY_NOT_IMPLEMENTED` rather than appearing silently supported.

### OPENAPI-AUDIT-004 — cross-session cache leakage

Resolved:

- reusable `ControlledSourceLoader` owns authority only;
- `SourceLoadingSession` owns reference bytes for one call;
- `ReferenceResolver` accepts only that session;
- duplicate references share one load within a call;
- a new call reloads controlled external documents;
- same adapter/source ID with changed content produces a fresh contract and digest.

### OPENAPI-AUDIT-005 — YAML alias recursion/expansion

Resolved with behavior-versioned options:

- `maxYamlDepth`;
- `maxYamlNodes`;
- `maxYamlAliases`.

The converter counts mapping keys and values, tracks active nodes, counts repeated alias expansion, and converts recursion/limit failures into stable diagnostics:

- `OA_PARSE_YAML_ALIAS_CYCLE`;
- `OA_LIMIT_YAML_DEPTH`;
- `OA_LIMIT_YAML_NODES`;
- `OA_LIMIT_YAML_ALIASES`;
- `OA_LIMIT_YAML_RECURSION`.

### OPENAPI-AUDIT-006 — missing package-level verification

Added:

- public source-adapter protocol and shared conformance tests;
- public import and factory smoke tests;
- entry-point invocation tests;
- standard OpenAPI 3.0 facade integration;
- JSON/YAML semantic/digest equivalence;
- cancellation and invalid-input behavior;
- cross-session and within-session reference behavior;
- default network denial and local path-escape tests;
- recursive/deep/expanded YAML tests;
- architecture/import ownership tests;
- wheel-content and isolated-wheel installation tests.

### OPENAPI-AUDIT-008 — missing typed metadata package reference

Resolved by removing the import of the nonexistent `codepotg_openapi.x_codegen` package. The normalization context keeps a private `None` placeholder only until OA-010 is implemented in a separate reviewed phase.

### OPENAPI-AUDIT-009 — external Path Item provenance

Resolved by using the resolved Path Item document when creating shape diagnostics and operation provenance.

## Version and digest identity

The repaired distribution is `2.0.0a2` / descriptor `2.0.0-alpha.2`. Adapter behavior identity is version `2` and includes:

- package, plugin API, and IR API versions;
- OpenAPI support policy;
- all decoded behavior options, including YAML limits;
- every loaded document's canonical semantic value;
- host reference-authority identity;
- no typed `x-codegen` version claim.

## Verification evidence available in this environment

Executed locally against the repair drafts:

- Python syntax/compile checks for changed source and tests;
- adversarial parser harness: **5/5 passed**;
- loading-session isolation harness: **3/3 passed**.

Committed tests target the actual sibling `codepotg-v2` public source tree and built wheels. They were not replaced with compatibility mocks.

## Required reviewer commands

From `packages/python/codepotg-openapi` in a synchronized repository checkout:

```bash
python -m pip install -e ../codepotg-v2 -e '.[dev]'
python -m ruff check src tests
python -m ruff format --check src tests
python -m pytest -q
python -m build
```

Then install the freshly built core and adapter wheels in a new environment and invoke `codepotg.source_adapters/openapi` under isolated Python. Mark OA-001/OA-017/OA-018 complete only after that evidence is appended to `docs/tasks/PROGRESS.md`.
