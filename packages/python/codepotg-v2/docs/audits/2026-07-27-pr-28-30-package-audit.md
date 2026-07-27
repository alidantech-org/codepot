# Package audit index — PRs #28, #29, and #30

**Audit date:** 2026-07-27  
**Target branch:** `chatgpt/codepotx-restart`  
**Packages:** Jinja, OpenAPI, TypeScript, Dart

This audit reviewed merged source, task plans, progress evidence, package boundaries, and PR metadata. It did not independently execute the Python test/build commands, so implementing-agent test counts are treated as recorded evidence rather than reproduced evidence.

## Executive matrix

| PR | Package | Architecture | Current-port implementation | Release readiness | Required action |
|---|---|---:|---:|---|---|
| #28 | `codepotg-template-jinja` | strong | high | review | Close exact Ruff/real-core/real-wheel gates; address two low compatibility/diagnostic items. |
| #29 | `codepotg-openapi` | directionally correct | foundation only | not usable | Critical repair: add missing adapter/facade, session isolation, YAML hardening, public conformance/distribution tests. |
| #30 | `codepotg-language-typescript` | strong | high | review | Fix direct option validation and reproduce exact release/wheel gates. |
| #30 | `codepotg-language-dart` | strong | high | review | Fix direct option validation, run real Dart SDK oracle, and reproduce exact release/wheel gates. |

## PR #28 — Jinja

### Result

The implementation respects the intended template-engine boundary:

- sandboxed strict rendering;
- immutable bounded contexts;
- static request-owned partial dependencies;
- no filesystem, network, environment, commands, writer, target syntax, or planner ownership;
- bounded streaming output;
- instance-owned cache;
- extensive recorded tests.

### Readiness

Safe to keep merged and use for continued integration. Not release-complete because its own PR/progress evidence said Ruff, synchronized real-core verification, and real-wheel verification were open when merged.

### Full report and fix handoff

```text
packages/python/codepotg-template-jinja/docs/audits/2026-07-27-pr-28-audit.md
packages/python/codepotg-template-jinja/docs/tasks/AUDIT_FIXES.md
```

## PR #29 — OpenAPI

### Result

Useful subsystems were merged:

- typed options;
- controlled local/memory loading;
- duplicate-key-aware parsing;
- reference resolution;
- stable IDs;
- substantial standard schema/group/operation normalization.

However, the package is not a functioning source adapter. The registered factory imports a missing `codepotg_openapi.adapter` module. There is no final composed `normalize()` pipeline or public source-adapter conformance path.

Additional critical/high issues:

- loader-owned cache can cross normalization sessions;
- YAML alias cycles/expansion are not explicitly bounded;
- no package-level entry-point, architecture, conformance, integration, distribution, or security suites were merged;
- README claims missing typed `x-codegen`, support, and benchmark work.

### Readiness

Safe to keep merged only as an explicitly unfinished foundation. Do not install or advertise it as a working OpenAPI source adapter.

### Full report and fix handoff

```text
packages/python/codepotg-openapi/docs/audits/2026-07-27-pr-29-audit.md
packages/python/codepotg-openapi/docs/tasks/AUDIT_FIXES.md
```

## PR #30 — TypeScript

### Result

The adapter remains correctly lightweight and non-rendering. Target descriptors, identifier/output validation, and relative/alias/package/explicit module facts are present and well separated.

Required code repair: direct `TypeScriptTargetOptions(...)` construction accepts raw string/non-enum policy values. Later identity comparisons silently ignore those values, producing unexpected behavior.

Distribution tests also need a non-skipping post-build artifact check.

### Readiness

Safe to keep merged. Apply the option fix before relying on host-constructed custom options. Release completion still requires the exact synchronized commands and real-wheel installation.

### Full report and fix handoff

```text
packages/python/codepotg-language-typescript/docs/audits/2026-07-27-pr-30-audit.md
packages/python/codepotg-language-typescript/docs/tasks/AUDIT_FIXES.md
```

## PR #30 — Dart

### Result

The adapter correctly validates Dart names/paths and produces relative, package, and explicit URI facts without Flutter or rendering assumptions.

Required code repair: direct `DartTargetOptions(...)` construction accepts raw string/non-enum policy values and may silently ignore them or fail later during introspection.

A real Dart SDK oracle remains a release gate, and artifact inspection must run after build rather than conditionally skip.

### Readiness

Safe to keep merged. Apply the option fix before custom host construction. Do not mark release-complete before the Dart SDK and real-wheel checks pass.

### Full report and fix handoff

```text
packages/python/codepotg-language-dart/docs/audits/2026-07-27-pr-30-audit.md
packages/python/codepotg-language-dart/docs/tasks/AUDIT_FIXES.md
```

## Task-ledger corrections made by this audit

- Jinja tasks now distinguish implemented current-port work from blocked named-output/pack/planner/cache-port integrations.
- OpenAPI tasks now identify the missing adapter/facade as a critical blocker and distinguish foundations from unimplemented semantics.
- TypeScript and Dart tasks now mark current-port implementations, blocked planner facts, required option repairs, and open release gates.
- Package progress files now contain independent audit rows.
- The shared parallel registry now routes each fixing lane to a one-slash feature branch and prevents false completion claims.

## Audit rule for all four packages

A merged PR is not automatically a completed task. Completion requires:

1. implemented acceptance behavior;
2. truthful blockers;
3. synchronized real-core verification;
4. lint and formatting;
5. build and post-build artifact inspection;
6. isolated real-wheel invocation;
7. required external compiler oracle where applicable;
8. clean scoped diff and recorded evidence.

No `.github` automation is required or permitted by this audit.
