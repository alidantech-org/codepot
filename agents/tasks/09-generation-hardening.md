# Phase 09 — Production-grade generation hardening

Status: [ ]
Issue: open after Phase 08
Depends on: template variable contract
Commits: pending
Validation: pending

## Goal

Bring generation to release grade by porting the strongest behavior from `codepotg`, enforcing deterministic planning and safe emission, and exposing complete reports for every decision.

## Tasks

- [ ] Port stable template context groups, naming sets, item emission metadata, file metadata, dependency purposes, and import facts from Python.
- [ ] Build an output index before rendering so templates can resolve dependency output paths and relative imports.
- [ ] Add language-neutral dependency collection and injected language import adapters.
- [ ] Support registered partials, raw/static files, hidden files, escaped path markers, and template-package metadata.
- [ ] Add strict duplicate-output detection and collision diagnostics.
- [ ] Add plan refusal for unsafe, protected, conflicting, or unresolved output paths.
- [ ] Add transactional staging and rollback for multi-file generation.
- [ ] Add stale managed-file cleanup through a generation manifest rather than broad directory deletion.
- [ ] Preserve immutable files and classify created, updated, unchanged, skipped, refused, deleted, and rolled-back outcomes.
- [ ] Add before/after command policies, optional command behavior, cancellation propagation, and output capture limits.
- [ ] Add deterministic reports, counters, durations, diagnostics, artifacts, and event coverage.
- [ ] Add incremental cache keys based on authoring, template, variable, and generator digests.
- [ ] Add equivalence tests for source, cached-artifact, and supplied in-memory artifact generation.

## Rules

- Rendering completes fully in memory before any write or cleanup.
- Generation never imports concrete authoring or templating implementations.
- Deletes are limited to previously managed files recorded in a manifest or explicit safe clean roots.
- A failed required command or write rolls back the current task when transactional mode is enabled.
- Deterministic inputs must produce byte-identical plans, reports, and virtual files.
