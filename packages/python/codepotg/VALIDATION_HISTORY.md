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

### Scope correction

The approximately five-second JSON and six-second YAML profiles reported after this checkpoint
used the bundled debug template pack. They proved the compiler, contract, rendering, batching,
and release behavior for that synthetic pack, but they did **not** prove Nest, Next, or Dart
production-template performance. Their generated files were written to a temporary profiler
directory and deleted at process exit.

The release-performance gate is therefore expanded to require the realistic Nest, Next, and
Dart fixture projects under `tests/fixtures/realistic_projects`, visible generated review
output, and profiles that pass both `--templates` and `--workspace`.

Next verification steps:

1. Run `tests/integration/test_realistic_template_packs.py`.
2. Run the complete suite and Ruff.
3. Generate visible review output for all three packs.
4. Profile each realistic pack and record exact output counts, RSS, private bytes, queue
   high-water marks, and durations.
5. Treat the debug profile only as synthetic engine evidence.
