# 03 — Generation, planning, and output safety

CodepotG v2 plans every pack file and every output before rendering or writing.

## Documents

- [`01-template-file-model.md`](01-template-file-model.md) — one descriptor per source file, template/barrel/static/binary/partial/documentation roles, target/engine inference, outputs, and authored barrels.
- [`02-selection-folder-patterns-and-static-files.md`](02-selection-folder-patterns-and-static-files.md) — once/each/grouped/aggregate/artifact selections, tokenized folder fan-out, profiles, and Gitignore-compatible exclusions.
- [`03-planning-execution-and-transaction.md`](03-planning-execution-and-transaction.md) — complete immutable plans, dependency graphs, invocations, path safety, writers, ownership, rollback, dry run, readiness, and cache.

## Processing pipeline

```text
load and decode typed v2 Project
→ resolve immutable pack snapshots
→ load typed v2 TemplatePack manifests
→ discover/classify files exactly once
→ normalize named sources into neutral IR
→ resolve selections, rules, bindings, dependencies, setup, and commands
→ create per-template/static invocations
→ build and validate all graphs and outputs
→ render/copy into staging or memory
→ compare exact content
→ commit transaction
→ run permitted post-commit actions
```

There is no global language pipeline. One `TemplateInvocation` has one target adapter, one engine adapter, one selected context or aggregate, typed effective rules, bindings, dependencies, and declared outputs.

## Safety summary

Before rendering, CodepotG validates:

- target and engine availability;
- include and artifact graph cycles;
- required/ambiguous providers;
- cross-target partial compatibility;
- rule and override permissions;
- bindings and readiness policy;
- command capabilities and approvals;
- path traversal, symlinks, case collisions, and duplicate destinations;
- managed/protected/immutable ownership conflicts.

Static files and binary assets pass through the same plan and writer safety model as rendered templates.
