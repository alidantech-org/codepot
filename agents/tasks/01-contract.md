# Phase 01 — Shared contract and stable artifacts

Status: [ ]
Issue: #3
Depends on: Phase 00
Commit: pending
Validation: pending

## Goal

Define the implementation-independent protocol that every engine, platform adapter, runtime, and frontend must obey.

## 01.1 Diagnostics and sources

- [ ] Define diagnostic codes, severity, locations, hints, and related diagnostics.
- [ ] Define portable source-file and source-range references.
- [ ] Define typed success and failure results across frontend boundaries.

## 01.2 Stable artifacts

- [ ] Define version headers and compatibility rules.
- [ ] Define `CompiledAuthoringArtifact`.
- [ ] Define `CompiledTemplatePack`.
- [ ] Define `GenerationPlan`, virtual files, rendered generation, and generation result.
- [ ] Prove required artifacts are deterministic, immutable, and JSON serializable.

## 01.3 Engine contracts

- [ ] Define authoring compile, validate, inspect, cache, and artifact-load requests/results.
- [ ] Define templating load, validate, compile, context, and render requests/results.
- [ ] Define generation load, plan, render, write, clean, command, and execute requests/results.
- [ ] Define `AuthoringPort`, `TemplatingPort`, and `GenerationPort` before implementations.

## 01.4 Platform contracts

- [ ] Define filesystem and in-memory filesystem operations.
- [ ] Define changed-aware and atomic writer contracts.
- [ ] Define YAML and JSON codec contracts.
- [ ] Define TypeScript module-loader contracts.
- [ ] Define local, package, repository, and artifact source-resolver contracts.
- [ ] Define hashing, cache, command-runner, clock, ID, and event-bus contracts.

## 01.5 Runtime and frontend protocol

- [ ] Define runtime request and result unions.
- [ ] Define typed event envelopes, event union, subscriptions, and disposal.
- [ ] Define cancellation and per-run context contracts.
- [ ] Define feature and capability discovery contracts.

## Acceptance criteria

- [ ] Shared contracts have no concrete platform or framework dependencies.
- [ ] Interfaces and method contracts exist before concrete implementations.
- [ ] Domain control flow does not depend on events.
- [ ] In-memory adapters can implement every required platform boundary.
- [ ] Typecheck passes.
- [ ] Contract review decisions are recorded.
- [ ] Commit SHA and validation evidence are recorded here.
- [ ] Issue #3 is closed only after all criteria pass.
