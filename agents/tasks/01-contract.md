# Phase 01 — Shared contract and stable artifacts

Status: [x]
Issue: #3 closed as completed
Depends on: Phase 00
Commits: `b5b2624a356c902ab4185f59bc2d2f37aefefa4f`, `7d5b44d9ee5f55e351db1d8bd96b2ee85006f71a`
Validation: strict TypeScript typecheck and declaration emission passed locally using the repository compiler flags; GitHub content reads and commit comparisons verified the published contract subpath and committed files.

## Goal

Define the implementation-independent protocol that every engine, platform adapter, runtime, and frontend must obey.

## 01.1 Diagnostics and sources

- [x] Define diagnostic codes, severity, locations, hints, and related diagnostics.
- [x] Define portable source-file and source-range references.
- [x] Define typed success and failure results across frontend boundaries.

## 01.2 Stable artifacts

- [x] Define version headers and compatibility rules.
- [x] Define `CompiledAuthoringArtifact`.
- [x] Define `CompiledTemplatePack`.
- [x] Define `GenerationPlan`, virtual files, rendered generation, and generation result.
- [x] Keep stable artifacts immutable and JSON-safe: no functions, classes, dates, maps, sets, buffers, or live Zod/Handlebars instances.

## 01.3 Engine contracts

- [x] Define authoring compile, validate, inspect, cache, and artifact-load requests/results.
- [x] Define templating load, validate, compile, context, and render requests/results.
- [x] Define generation load, plan, render, write, clean, command, and execute requests/results.
- [x] Define `AuthoringPort`, `TemplatingPort`, and `GenerationPort` before implementations.

## 01.4 Platform contracts

- [x] Define filesystem and in-memory filesystem operations.
- [x] Define changed-aware and atomic writer contracts.
- [x] Define YAML and JSON codec contracts.
- [x] Define TypeScript module-loader contracts.
- [x] Define local, package, repository, artifact, and memory source-resolver contracts.
- [x] Define hashing, encoded cache, command-runner, clock, ID, and event-bus contracts.

## 01.5 Runtime and frontend protocol

- [x] Define a typed runtime operation map and inferred request/result unions.
- [x] Define typed event envelopes, event union, subscriptions, and disposal.
- [x] Define cancellation and per-run context contracts.
- [x] Define feature and capability discovery contracts.
- [x] Export the contract from the package root and `codepotx/contract`.

## Contract decisions

- Stable authoring is the canonical source consumed by templating and generation; OpenAPI is not an intermediate contract.
- Required control flow uses typed ports and returned results. Events are observational only.
- The runtime is represented by `CodepotRuntimePort`; frontends do not access engine internals.
- Platform I/O is inverted behind explicit interfaces and can be replaced by in-memory adapters.
- Cache storage uses encoded text/base64 payloads so stable artifacts are serialized explicitly through the codec port.
- Artifact headers contain protocol, artifact, producer, content-digest, and source-digest information without nondeterministic timestamps.

## Acceptance criteria

- [x] Shared contracts have no concrete Node, Zod, Handlebars, YAML, Git, shell, or CLI dependencies.
- [x] Interfaces and method contracts exist before concrete implementations.
- [x] Domain control flow does not depend on events.
- [x] In-memory adapters can implement every required platform boundary.
- [x] Strict typecheck passes.
- [x] Declaration emission passes with isolated declarations.
- [x] Contract review decisions are recorded.
- [x] Commit SHA and validation evidence are recorded here.
- [x] Issue #3 closed after all criteria passed.

## Validation evidence

- `tsc` 5.8.3 passed with the repository's strict, isolated-module, isolated-declaration, exact-optional, no-unused, and no-unchecked compiler flags.
- Declaration-only emission produced declarations for the root and every contract module.
- GitHub comparison from `ae80518a45aae359314f1b93b397131025f62c39` to `b5b2624a356c902ab4185f59bc2d2f37aefefa4f` verified all contract files and package export changes.
- GitHub comparison from `b5b2624a356c902ab4185f59bc2d2f37aefefa4f` to `7d5b44d9ee5f55e351db1d8bd96b2ee85006f71a` verified the cache and complete runtime-operation corrections.
- GitHub content reads verified `codepotx/contract`, `CompiledAuthoringArtifact`, engine ports, and the complete runtime operation map.
- Full `pnpm check` remains a repository-level packaging gate for Phase 07 because the connector environment cannot install the pinned workspace dependencies.
