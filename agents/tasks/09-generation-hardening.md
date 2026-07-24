# Phase 09 — Production-grade generation hardening

Status: [ ]
Issue: open after Task 24 direction gates are approved
Depends on: template variable contract and Task 24 architecture decisions
Commits: pending
Validation: pending

## Goal

Bring generation to release grade without retaining the old assumption that the complete OpenAPI document, complete generation plan, and all rendered files must exist in memory before writing begins.

Task 24 is the detailed source of truth for the CodepotG JSONL-first, lazy-selection, explicit-dependency, queue-based generation architecture. This phase remains the umbrella for safe emission, lifecycle behavior, reports, cache integrity, commands, and release-grade validation.

## Ordered work

1. Complete the JSONL compilation and headless-indexing foundation from Task 24.
2. Obtain human approval for the new `paths.yaml` direction before implementing its contract.
3. Implement selection-aware planning, explicit dependency providers, barrels, lazy context, and incremental output.
4. Reapply production safety, managed lifecycle, reporting, commands, and deterministic cache behavior over the new pipeline.
5. Update template-author documentation and run release-grade memory and concurrency gates.

## Tasks

- [ ] Keep stable template context groups, naming sets, item emission metadata, file metadata, dependency purposes, and import facts, but expose them through selection-specific lazy contexts.
- [ ] Replace the mandatory global output-index pass with a bounded virtual/written output registry populated as selections and emissions are planned.
- [ ] Add language-neutral dependency collection and injected language import adapters.
- [ ] Require explicit dependency providers and validate that each provider can emit the requested concept and item.
- [ ] Add effective-provider conflict validation, including transitive symbols exposed by barrels.
- [ ] Add dynamic barrel scheduling based on exported emission completion.
- [ ] Support registered partials, raw/static files, hidden files, escaped path markers, and template-package metadata.
- [ ] Add strict duplicate-output, duplicate-selection, ambiguous-provider, and collision diagnostics.
- [ ] Add plan refusal for unsafe, protected, conflicting, unresolved, or non-normalized output paths.
- [ ] Preserve atomic generated-file writes and bounded write queues.
- [ ] Add stale managed-file cleanup through a generation manifest rather than broad directory deletion.
- [ ] Preserve immutable files and classify created, updated, unchanged, skipped, refused, deleted, and failed outcomes.
- [ ] Add before/after command policies, optional command behavior, cancellation propagation, and output capture limits.
- [ ] Add deterministic reports, counters, durations, diagnostics, artifacts, queue state, and event coverage.
- [ ] Add incremental cache keys based on source, JSONL line/section, index, template, variable, selection, dependency-provider, and generator digests.
- [ ] Add equivalence tests for source, cached-index, and supplied-record generation.
- [ ] Add bounded-memory and progressive-file-visibility tests for large OpenAPI JSON fixtures.

## Rules

- JSON is the preferred OpenAPI input; YAML remains a warned compatibility path.
- The full OpenAPI document is not required in memory.
- The full rendered project is not required in memory.
- Planning, rendering, writing, and event logging may overlap through bounded queues.
- A lightweight dependency/output graph may exist in memory, but raw records and rendered blobs remain bounded and evictable.
- Generated files are written atomically.
- Success is reported only after required queues drain and writer errors are checked.
- Deletes are limited to previously managed files recorded in a manifest or explicit safe clean roots.
- Deterministic inputs must produce byte-identical JSONL records, indexes, registry facts, reports, and generated files.
- `paths.yaml` syntax and semantics must not be finalized without explicit human approval.
