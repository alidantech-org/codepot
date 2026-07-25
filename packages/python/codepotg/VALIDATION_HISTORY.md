# CodepotG Validation History

Branch: `chatgpt/codepotx-restart`

This file records locally executed validation evidence reported from the Windows development environment. A checkpoint is recorded only after the command output has been shared and reviewed.

## 2026-07-25 — SQLite, JSONL, batching, and normalized-contract checkpoint

Validated branch head before this documentation commit:

```text
57b7a5ea7e315984a4bd1c0faf99da66a43e4ab0
```

Focused performance and cache gate:

```text
Ruff: all checks passed
Tests: 23 passed
Duration: 19.57 seconds
```

The focused gate covered:

- JSONL compilation and cache reuse;
- SQLite-backed indexes;
- lazy selection and reduced-document reconstruction;
- YAML compatibility conversion and cache upgrades;
- bounded and batched graph writes;
- end-to-end debug generation;
- normalized graph generation.

Complete package gate:

```text
Tests: 351 passed
Duration: 32.11 seconds
Ruff: all checks passed
```

Observed outcome:

- no remaining focused or full-suite failures;
- the earlier SQLite thread-ownership failure is resolved;
- YAML compatibility cache rebuilding preserves `source.json`;
- Jinja templates remain cached within one generation but refresh between emissions;
- milestone-only JSONL progress avoids per-record callback overhead;
- full-suite execution is substantially faster than the earlier approximately 55–100 second runs.

Next verification steps:

1. Run non-`--full` JSON and YAML speed profiles.
2. Record RSS, private bytes, adaptive queue limits, batch high-water marks, and per-stage durations.
3. Reconcile `CODEPOTG_READINESS_TASKS.md`, `NORMALIZED_CONTRACT_VERIFICATION_TASKS.md`, and Task 24 from the measured profile evidence.
