# Isolated v1/v2 Jinja benchmarks

These runners compare neutral rendering behavior without importing CodepotG v1 and v2 into one interpreter. Correctness, sandbox safety, bounded resources, and structured failures take priority over speed.

## Cases

Both runners cover scalar interpolation, nested mapping lookup, conditional branches, 100-item and 1,000-item loops, macro invocation, one include, an eight-level include chain, inheritance, large deterministic output, strict-undefined failure, syntax failure, and 100 repeated warm renders.

Each runner performs one warm-up and seven measured cold and warm iterations. JSON includes output SHA-256, output bytes, all durations, median and maximum duration, process peak RSS where the platform exposes it, and cache observations. Private bytes are not emitted when the standard library cannot report them portably.

## Run v1 only in a CodepotG 1.0.0 environment

```bash
cd packages/python/codepotg
python -m venv .benchmark-v1
. .benchmark-v1/bin/activate
python -m pip install -e .
python ../codepotg-template-jinja/benchmarks/run_v1_baseline.py \
  > ../codepotg-template-jinja/benchmark-results/v1.json
```

On Windows PowerShell, activate with `.benchmark-v1\Scripts\Activate.ps1`.

## Run v2 only in a CodepotG v2/Jinja environment

```bash
cd packages/python/codepotg-template-jinja
python -m venv .benchmark-v2
. .benchmark-v2/bin/activate
python -m pip install -e ../codepotg-v2
python -m pip install -e .
python benchmarks/run_v2_engine.py > benchmark-results/v2.json
```

## Compare

```bash
python benchmarks/compare_results.py \
  benchmark-results/v1.json \
  benchmark-results/v2.json
```

`benchmark-results/` is ignored. Do not commit machine-specific timings. Output parity is expected for successful neutral cases. Failure rows are not security-parity claims: v2 intentionally returns structured diagnostics and applies stronger sandbox rules, while v1 raises ordinary Jinja exceptions.
