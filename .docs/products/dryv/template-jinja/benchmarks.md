# Jinja v1/v2 benchmarks

These runners compare neutral rendering behavior without importing the legacy v1 renderer and the active Dryv v2 Jinja adapter into one interpreter. Correctness, sandbox safety, bounded resources, and structured failures take priority over speed.

The benchmark source remains under `packages/python/dryv-template-jinja/benchmarks/`; this document is its canonical operating guide.

## Cases

Both runners cover scalar interpolation, nested mapping lookup, conditional branches, 100-item and 1,000-item loops, macro invocation, one include, an eight-level include chain, inheritance, large deterministic output, strict-undefined failure, syntax failure, and 100 repeated warm renders.

Each runner performs one warm-up and seven measured cold and warm iterations. JSON includes output SHA-256, output bytes, all durations, median and maximum duration, process peak RSS where the platform exposes it, and cache observations. Private bytes are not emitted when the standard library cannot report them portably.

## Run the legacy v1 baseline

The v1 runner imports the earlier `emission.templates.renderer` implementation. Provide a checkout or source distribution containing that legacy package as `DRYV_V1_SOURCE`; do not point it at the active `packages/python/dryv` package.

Create an isolated environment without activation:

```bash
uv venv .benchmark-envs/v1 --python 3.11 --no-project
uv pip install \
  --python .benchmark-envs/v1/bin/python \
  "$DRYV_V1_SOURCE"
.benchmark-envs/v1/bin/python \
  packages/python/dryv-template-jinja/benchmarks/run_v1_baseline.py \
  > packages/python/dryv-template-jinja/benchmark-results/v1.json
```

On Windows, use `.benchmark-envs\v1\Scripts\python.exe` for the two Python-path arguments. No environment activation is required.

## Run the active v2 adapter

From the repository root:

```bash
uv run --all-packages python \
  packages/python/dryv-template-jinja/benchmarks/run_v2_engine.py \
  > packages/python/dryv-template-jinja/benchmark-results/v2.json
```

## Compare

```bash
uv run --all-packages python \
  packages/python/dryv-template-jinja/benchmarks/compare_results.py \
  packages/python/dryv-template-jinja/benchmark-results/v1.json \
  packages/python/dryv-template-jinja/benchmark-results/v2.json
```

`benchmark-results/` is ignored. Do not commit machine-specific timings. Output parity is expected for successful neutral cases. Failure rows are not security-parity claims: v2 intentionally returns structured diagnostics and applies stronger sandbox rules, while v1 raises ordinary Jinja exceptions.
