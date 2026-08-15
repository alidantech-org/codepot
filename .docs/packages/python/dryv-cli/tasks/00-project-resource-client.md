# Task 00 — Refactor CLI into a Project Client resource collector

Status: [ ]
Owner: `packages/python/dryv-cli`
Depends on: Dryv Project/Resources contracts and `dryv-api` build HTTP API
Validation: workspace/resource collection tests, no-engine-import tests

## Goal

Make `dryv-cli` a Project Client rather than an in-process generator frontend. The CLI runs in the user's project, owns local resource discovery/acquisition, and sends a portable resource bundle to `dryv-api`.

## Project-side responsibilities

The CLI must be able to:

- discover the project `dryv.yaml` from the invocation/workspace rules;
- read only enough project configuration locally to discover required resources and connection settings;
- collect serialized IR resources when precompiled IR is configured;
- collect author source resources when an Author Backend is configured;
- resolve local pack manifests/templates;
- resolve Git-hosted packs using the user's normal Git credentials/process outside Dryv Engine;
- compute content hashes for collected resources;
- build a logical ResourceManifest with project-relative/logical IDs;
- read the previous local managed-output manifest;
- send `dryv.yaml`, resource manifest and previous managed outputs to `dryv-api`;
- upload only resources the API reports missing.

## Resource safety

- normalize all workspace paths against an explicit project root;
- reject path traversal outside allowed project/pack roots unless explicitly configured as an external resource with a safe logical identity;
- never send Git credentials themselves to Dryv/API;
- do not use absolute host paths as canonical resource IDs;
- preserve content hashes so remote builds can reuse unchanged blobs.

## CLI/engine boundary

`dryv-cli` must not import Runtime internals or execute generation features directly in normal operation.

The CLI may use generated/shared API protocol types. It owns presentation, commands, local project discovery and project-side effects.

## Non-goals

- Do not apply generated files yet; Task 02 owns local writes.
- Do not implement progress/artifact WebSocket streaming yet; Task 01 owns transport/build stream.
- Do not execute author/template implementations inside CLI.

## Allowed paths

- `packages/python/dryv-cli/**`
- `.docs/packages/python/dryv-cli/**`
- shared/generated API protocol artifacts used by CLI

## Acceptance criteria

- CLI can turn a fixture project into a deterministic logical ResourceManifest.
- local/private pack acquisition happens client-side.
- only missing resource blobs are uploaded in an integration fixture.
- previous managed-output state is included in build start.
- CLI normal generation path has no direct Dryv Runtime orchestration dependency.

## Validation

Test project-root discovery, `dryv.yaml` collection, precompiled IR, author-source resources, local packs, private/local Git pack fixture, hash reuse, path traversal refusal and no-engine-import boundaries. Run CLI tests and `git diff --check`.
