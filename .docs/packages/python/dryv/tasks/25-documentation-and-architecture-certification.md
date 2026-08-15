# Task 25 — Certify Dryv documentation and architecture after migration

Status: [ ]
Owner: `packages/python/dryv`
Depends on: Tasks 21–24 and all participating external package migrations
Validation: documentation link checks, architecture tests, full workspace verification

## Goal

After the new architecture is proven, make active documentation describe only the real system and certify that package/code boundaries match the approved design.

## Canonical architecture documentation

Document the final active flow:

```text
Author Backend
    ↓ Canonical Dryv IR

Project Client
    ↓ dryv.yaml + resources + previous managed outputs

dryv-api
    ↓
Dryv Runtime
    ↓ coordinates independent Features
    ↓
AuthorSession / RenderSession as required
    ↓
Artifact + WriteInstruction stream
    ↓
dryv-api
    ↓
Project Client
    ↓
user filesystem apply
```

## Required contracts to document separately

### Canonical IR contract

Cover the canonical concept family and relationships, including:

- Contract/Group/Property;
- Schema, field capabilities and approved single-base extension;
- Policy/Failure/Event/Operation;
- StorageMapping/ValueSource/View;
- Workflow/Presentation;
- tags/guidance/provenance/typed refs;
- authored forward versus Runtime-derived reverse relationships.

### Author Backend contract

Explain direct JSON/YAML/JSONL output plus optional HTTP/WS service/registration modes.

### Pack contract

Explain `dryv.pack.yaml`, selection/context/artifact relationships and renderer capability requirements using only approved vocabulary.

### Render Client contract

Explain template + canonical JSON context → generated logical output bytes, renderer fingerprinting, HTTP mode and outbound WS registration.

### Project/API contract

Explain `dryv.yaml`, logical resources, content-addressed transfer, previous managed outputs, build events, artifact streaming and local safe apply.

## Deployment examples

Document and test examples for:

```text
local CLI + local dryv-api + local Render Client
local CLI + remote dryv-api
remote dryv-api + outbound local Render Client
precompiled IR
Python Author Backend
web/playground preview/download
VS Code/Node Project Client
cache use/refresh/off
dry-run/plan
cancellation/failure/reconnect
```

## Remove stale active docs

Active docs must not describe superseded plugin/runtime-write paths as current. Historical documents may remain archived/brainstormed according to repository rules but must not be linked as canonical current architecture.

Update package READMEs for `dryv`, `dryv-author`, `dryv-cli`, `dryv-api`, Jinja Render Client, Handlebars Render Client and TypeScript Dryv Client.

## Architecture certification

Add/complete tests that fail when:

- canonical IR appears outside its authority;
- Features reach upward into Runtime;
- engine code hosts API server behavior;
- project-write code reappears in Dryv Engine;
- Render/Author implementations import engine internals;
- CLI/TS frontends bypass API and orchestrate Runtime directly;
- protocol specs and generated client models drift.

## Non-goals

- Do not introduce new architecture during certification.
- Do not publish marketplace/product marketing docs in this task.

## Allowed paths

- canonical `.docs/packages/**` documentation for participating Dryv packages
- package READMEs
- architecture/protocol conformance tests
- `.docs/TODO.md` and task archival paths according to task rules

## Acceptance criteria

- active docs and source architecture agree.
- all reference flows are documented and validated.
- no stale active architectural path contradicts the implemented system.
- architecture tests enforce the final boundaries.
- task completion/archival follows repository rules.

## Validation

Run all participating Python/Node package tests, architecture/protocol conformance tests, docs/link checks available in the repository, generated-client drift checks, and `git diff --check`. Record exact commands/evidence before closing the migration.
