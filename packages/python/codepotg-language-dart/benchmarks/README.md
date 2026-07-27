# Dart isolated benchmarks

Run v1 and v2 in separate environments/processes. Each runner prints plain JSON, performs one warm-up and seven measured runs over deterministic 10,000-operation batches, and returns nonzero when required imports or cases fail.

```bash
python benchmarks/run_v1_baseline.py > v1.json
python benchmarks/run_v2_adapter.py > v2.json
python benchmarks/compare_results.py v1.json v2.json
```

The v1 environment must contain the old `codepotg` 1.0.0 distribution. The v2 environment must contain `codepotg-core` plus only this adapter. Do not install both CodepotG generations in one interpreter. Machine-specific outputs belong under ignored `benchmark-results/`.
