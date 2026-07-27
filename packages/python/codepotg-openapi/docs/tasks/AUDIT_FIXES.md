# Critical audit fix handoff — `codepotg-openapi`

This package is merged as an unfinished foundation. It is not a working source adapter until the critical items below are fixed.

## Branch

```text
Base: chatgpt/codepotx-restart
Fix branch: chatgpt/codepotx-restart-openapi-audit-fixes
```

Use exactly one slash. Do not create another branch. Do not modify `.github/**`.

## Mandatory reading

```text
packages/python/codepotg-openapi/docs/audits/2026-07-27-pr-29-audit.md
packages/python/codepotg-openapi/docs/design/README.md
packages/python/codepotg-openapi/docs/tasks/00-package-plan.md
packages/python/codepotg-openapi/docs/tasks/PROGRESS.md
packages/python/codepotg-v2/docs/00-governance/00-approved-architecture.md
packages/python/codepotg-v2/docs/00-governance/04-closed-semantic-kernel.md
packages/python/codepotg-v2/src/codepotg/ports/source.py
```

## Phase 1 — make the installed package real

1. Add `src/codepotg_openapi/adapter.py` implementing the public `SourceAdapter` protocol.
2. Compose one normalization session per `normalize()` call:

```text
options
→ controlled root load
→ parse/structure validation
→ session reference resolver
→ standard normalization
→ immutable Contract
→ codepotg.ir.validate_contract
→ deterministic digest
→ SourceAdapterResult
```

3. Add import-smoke and entry-point tests proving:

```python
entry.load()()
from codepotg_openapi import OpenApiSourceAdapter
```

4. Pass `assert_source_adapter_conformance` through the real public facade.
5. Ensure invalid input returns diagnostics instead of raw internal exceptions.

## Phase 2 — fix session isolation

1. Remove cross-normalization state from `ControlledSourceLoader._reference_cache`.
2. Make reference document caching operation/session-owned.
3. Prove the same adapter instance can normalize two requests with the same source ID but different content without stale results.
4. Prove a host-controlled reference loader is called again in a new normalization session.
5. Keep parse-once/reference-once behavior inside one session.

## Phase 3 — harden YAML

1. Detect active YAML node recursion/alias cycles.
2. Add maximum YAML conversion depth and item/node limits.
3. Prevent alias expansion bombs from causing unbounded conversion.
4. Convert `RecursionError` and limit failures into stable `OA_PARSE_*`/`OA_LIMIT_*` diagnostics.
5. Add adversarial recursive-alias and expansion fixtures.

## Phase 4 — truthful support boundary

1. Correct `README.md` so it describes only merged behavior.
2. Do not claim typed `x-codegen` until the versioned decoder exists.
3. Do not link to support/benchmark files before they exist.
4. Add `docs/support/README.md` and benchmarks only with tested implementation.
5. Update `docs/tasks/PROGRESS.md` after every coherent batch.

## Phase 5 — continue the planned adapter

After the public facade is stable, implement the remaining tasks in order:

```text
OA-009 security/access
OA-010 typed x-codegen
OA-011 storage
OA-012 views
OA-013 events/listeners
OA-014 execution hooks
OA-015 workflows/compensation
OA-016 full provenance/bounded preservation
OA-019 realistic/performance fixtures
OA-020 release
```

Do not combine all remaining semantics into one unreviewable commit.

## Required tests

```text
tests/contracts/test_source_adapter_contract.py
tests/architecture/test_boundaries.py
tests/security/test_yaml_alias_limits.py
tests/integration/test_standard_openapi.py
tests/integration/test_reference_session_isolation.py
tests/distribution/test_entry_point.py
tests/distribution/test_wheel_install.py
```

Names may vary, but all behaviors must be covered.

## Allowed scope

```text
packages/python/codepotg-openapi/**
packages/python/codepotg-v2/docs/tasks/PARALLEL_WORK.md
```

Do not modify core implementation files to make the package pass. Record exact public-core blockers.

## Completion gate for the critical fix

- entry-point factory loads;
- public import works;
- conformance passes;
- two-session isolation tests pass;
- YAML recursive/expansion attacks fail safely;
- a real OpenAPI document returns a valid immutable `Contract`;
- diagnostics and digest are deterministic;
- Ruff, format, complete tests, build, wheel/sdist, and isolated install pass;
- working tree is clean;
- exact evidence is appended to progress.
