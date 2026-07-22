# Python parity matrix

This file is the migration checklist for behavior borrowed from `codepotg` and the earlier archived Python pipeline.

| Python capability | TypeScript owner | Status |
|---|---|---|
| Stable typed template context | templating | planned |
| Template variable listing | templating/runtime/CLI | planned |
| Template selection validation | templating | planned |
| `{group}` folders and `[expression]` paths | templating | implemented; hardening planned |
| Escaped folder/dynamic markers | templating | planned |
| Static/raw and hidden files | templating | partial; hardening planned |
| Template partials | templating | planned |
| Dependency purposes and targets | templating | planned |
| Output index | generation | planned |
| Relative import resolution | templating + injected language adapter | planned |
| Per-file context | generation/templating | planned |
| Managed and immutable lifecycle | generation/writer | implemented; manifest hardening planned |
| Safe cleanup | generation | implemented; managed-manifest hardening planned |
| Dry run | generation | implemented |
| Before/after commands | generation/platform | implemented; policy hardening planned |
| Deterministic pass reports | generation/runtime | planned |
| Diagnostics counters and durations | generation/runtime | planned |
| Incremental no-change generation | generation/writer/cache | partial; hardening planned |
| Rollback | generation/writer | planned |
| Language adapters | templating/generation ports | planned |
| Context/report documentation | root docs + site | planned |

The TypeScript implementation may improve names and internal design, but it must preserve useful behavior and keep stable artifacts backward-migratable.
