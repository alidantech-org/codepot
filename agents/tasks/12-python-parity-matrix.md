# Python parity and evolution matrix

This file tracks useful behavior borrowed from `codepotg` and the earlier archived Python pipeline, plus the intentional improvements defined by Task 24.

| Capability | Owner | Status |
|---|---|---|
| Stable typed template context | templating | implemented baseline; lazy selection-specific context planned |
| Template variable listing | templating/runtime/CLI/docs | implemented baseline; selection catalog expansion planned |
| Template selection validation | templating | implemented baseline; canonical selection and grouping validation planned |
| `{group}` folders and `[expression]` paths | templating | implemented; approved `paths.yaml` redesign pending |
| Escaped folder/dynamic markers | templating | planned |
| Static/raw and hidden files | templating | implemented baseline; queue integration planned |
| Template partials | templating | implemented baseline |
| JSON-first streaming input | CodepotG compiler | Task 24 planned |
| YAML compatibility warning | CodepotG compiler/CLI | Task 24 planned |
| Raw section JSONL cache | CodepotG compiler/cache | Task 24 planned |
| Per-line and section hashing | CodepotG compiler/cache | Task 24 planned |
| Byte-offset JSONL lookup | CodepotG resolver | Task 24 planned |
| Headless ref and mention indexes | CodepotG indexing | Task 24 planned |
| Resource registry and ownership indexes | CodepotG indexing | Task 24 planned |
| Forward and reverse dependency indexes | CodepotG indexing | Task 24 planned |
| Bounded in-memory hot indexes | CodepotG cache/resolver | Task 24 planned |
| Bounded reader/writer/event queues | CodepotG generation/platform | Task 24 planned |
| Progressive file emission | CodepotG generation/writer | Task 24 planned |
| Explicit dependency providers | templating/generation | Task 24 planned after human approval |
| Effective barrel/provider conflict validation | templating/generation | Task 24 planned after human approval |
| Dynamic barrel scheduling | generation | Task 24 planned after human approval |
| Virtual and written output registry | generation | Task 24 planned |
| Relative import resolution | templating + injected language adapter | baseline exists; explicit-provider rewrite planned |
| Per-file context | generation/templating | baseline exists; lazy bounded rewrite planned |
| Managed and immutable lifecycle | generation/writer | implemented; queue/manifest hardening planned |
| Safe cleanup | generation | implemented; managed-manifest hardening planned |
| Dry run | generation | implemented |
| Before/after commands | generation/platform | implemented; policy hardening planned |
| Deterministic pass reports | generation/runtime | partial; queue/index coverage planned |
| Diagnostics counters and durations | generation/runtime | partial; stage and queue metrics planned |
| Incremental no-change generation | generation/writer/cache | partial; JSONL/index digest hardening planned |
| Rollback | generation/writer | implemented baseline; incremental pipeline semantics pending |
| Language adapters | templating/generation ports | implemented baseline; import-provider expansion planned |
| Context/report documentation | root docs + site + CodepotG docs | Task 24 final documentation phase |

The implementation may improve names and internals, but it must preserve useful behavior, keep stable artifacts migratable where approved, and never silently retain an old full-memory architecture when Task 24 explicitly replaces it.
