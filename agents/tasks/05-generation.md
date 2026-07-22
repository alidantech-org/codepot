# Phase 05 — Generation and CodepotFile orchestration

Status: [ ]
Issue: open when authoring and templating ports are usable
Depends on: Phases 01-04
Commit: pending
Validation: pending

## Goal

Port the important `codepotg` generation workflow while consuming authoring and templating only through injected ports.

## 05.1 CodepotFile

- [ ] Define CodepotFile, defaults, task, source, command, output, cleanup, and environment contracts before implementation.
- [ ] Load `CodepotFile.yml` with optional `.yaml` compatibility.
- [ ] Require explicit `allow: true` before commands, cleanup, or writing.
- [ ] Resolve defaults and named tasks deterministically.
- [ ] Support one task, selected task, and all-task execution.

## 05.2 Orchestration

- [ ] Resolve authoring source through `AuthoringPort`.
- [ ] Resolve template source through `TemplatingPort`.
- [ ] Keep source compilation and template compilation reusable outside CodepotFile execution.
- [ ] Run approved before commands through `CommandRunnerPort`.
- [ ] Produce one deterministic generation plan before rendering or writing.
- [ ] Render virtual files in memory through `TemplatingPort`.
- [ ] Write only through `FileWriterPort`.
- [ ] Run approved after commands after successful writes.

## 05.3 Lifecycle and safety

- [ ] Port managed and immutable file behavior.
- [ ] Port created, updated, unchanged, skipped, immutable-created, immutable-skipped, and refused classifications.
- [ ] Port exact, layout-insensitive, and raw/binary comparisons.
- [ ] Normalize text newlines and final newline where configured.
- [ ] Use atomic replacement for managed updates.
- [ ] Port safe cleanup checks for filesystem root, home, config root, output root, protected roots, immutable roots, and clean roots.
- [ ] Support dry run without filesystem mutation or command execution.

## 05.4 Events and results

- [ ] Publish typed task, source, planning, rendering, writing, cleanup, command, and completion events.
- [ ] Return structured diagnostics and complete per-task results.
- [ ] Keep events observational and preserve explicit control flow.
- [ ] Propagate cancellation through all long-running operations.

## 05.5 Validation

- [ ] Compare task selection and defaults against Python fixtures.
- [ ] Compare planning, write classifications, immutable behavior, refusals, cleanup, commands, and diagnostics.
- [ ] Verify direct programmatic generation without `CodepotFile.yml`.
- [ ] Verify complete in-memory generation with no disk writes.
- [ ] Typecheck, tests, build, and package validation pass.
- [ ] Record issue, commit, and evidence before marking complete.
