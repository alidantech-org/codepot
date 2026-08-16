# Dryv helper rewrite tasks

Status: APPROVED FOR IMPLEMENTATION
Branch: `develop` only
Scope: `packages/python/dryv-api/.helpers/{dryv-author,dryv-template-jinja,dryv-cli}`

This file is the authoritative implementation sequence for the helper packages that make the new Dryv API usable as one simple local developer experience.

## Non-negotiable architecture

```text
Authoring source
    ↓
dryv-author
    ↓
Canonical Dryv Runtime IR
    ↓
dryv-cli collects dryv.yaml + IR + local pack bundles
    ↓
dryv-api
    ↓
Dryv Runtime → GenerationPlan
    ↓
dryv-api preflight/scheduling
    ↓
Render Client(s), e.g. dryv-template-jinja
    ↓
artifact stream or deterministic bundle
    ↓
dryv-cli verifies/diffs/stages/applies
    ↓
local filesystem
```

The normal user experience remains `dryv validate`, `dryv compile`, `dryv plan`, and `dryv generate`. Local API and renderer processes may be started temporarily and torn down by the CLI; users must not need to understand ports, renderer registration, HTTP, WebSockets, or process topology.

## Universal enforcement rules

1. Work directly on `develop`. Never create a branch.
2. Production code only during HELPER-01 through HELPER-17. Do not add, modify, delete, regenerate, or run tests until the explicit review gate after HELPER-17 is approved.
3. Existing helper code, `.archives/deprecated`, and `packages/nodejs/codepot-openapi` are reference material only. Learn useful concepts; do not preserve old APIs, wire formats, names, session models, stdio modes, or behavior merely for compatibility.
4. No compatibility shims, aliases, migration facades, dual old/new modes, deprecated exports, or translation layers for removed contracts.
5. Keep modules focused and direct. Production source files should target <= 500 lines. Split by real responsibility before crossing that boundary; never create generic `utils.py`, `helpers.py`, `common.py`, or service-locator dumping grounds to evade it.
6. Authoring defines software meaning and compiles it into Canonical IR. It must not select packs, know templates/renderers/output paths, generate application source, or write generated project files.
7. Canonical Dryv Runtime IR remains the only semantic authority. Author declarations are ergonomic source-language structures, not a competing IR.
8. `dryv-api` owns renderer-neutral transport/preflight/scheduling. Render clients implement that protocol; they do not duplicate it.
9. Render clients receive template + canonical context contract/context and return generated artifact bytes/chunks. They do not interpret Canonical IR or mutate the user's filesystem.
10. `dryv-cli/filesystem` is the only helper owner of local generated-file mutation.
11. CLI resolvers resolve where inputs/resources come from. Runtime resolves what they mean. Never move semantic selection/planning/context construction into the CLI.
12. Preserve determinism, explicit references, provenance, diagnostics, cancellation, hash verification, bounded streaming/backpressure, safe paths, and atomic local application.
13. No hidden plugin discovery or semantic magic. Compiler feature order and process orchestration must be explicit and inspectable.
14. Do not add empty architecture for hypothetical features. The approved folders below are required because their capabilities are required; further folders need concrete responsibility before creation.

## Required dryv-author architecture

`dryv_author` must be folder-based with these owners: `api/`, `core/`, `features/`, `compiler/`, `validation/`, `loading/`, and `host/`.

Required feature modules: `properties`, `schemas`, `operations`, `failures`, `events`, `workflows`, `storage`, `policies`, `views`, `presentations`, `sources`, and `groups`.

Required compiler owners: `context/`, `naming/`, `resolvers/`, `passes/`, plus a small compiler/pipeline composition root.

Required semantic capabilities include reusable properties; typed references; schema projections such as pick/omit/partial; operations with inputs/outputs/effects/facets; first-class failures and events; storage mappings; value sources with dependencies/search/value/labels; policies; workflows with steps/transitions/decisions and operation/event relationships; views; presentations; groups/ownership/composition; deterministic naming/semantic IDs; author diagnostics; and canonical IR compilation.

Compiler pipeline:

```text
REGISTER
→ VALIDATE DECLARATIONS
→ RESOLVE REFERENCES
→ RESOLVE DERIVED AUTHORING
→ COMPILE FEATURES
→ ASSEMBLE GROUPS
→ CREATE CONTRACT
→ CANONICAL IR VALIDATION
→ Contract
```

`CompilerContext` owns author metadata, declaration/symbol/name/ownership registries, resolved references, normalized declarations, compiled canonical items, and diagnostics. Feature-specific resolution belongs with the feature; only cross-feature concerns belong in compiler-wide resolvers.

## Required dryv-template-jinja architecture

Keep this helper intentionally small:

```text
dryv_template_jinja/
├── renderer/
│   ├── environment.py
│   ├── validation.py
│   ├── rendering.py
│   └── fingerprint.py
└── client/
    └── connection.py
```

Preserve the useful ideas of `SandboxedEnvironment`, `StrictUndefined`, deterministic renderer fingerprinting, and cancellation checkpoints. Remove old RenderSession/stdio/duplicated protocol architecture.

## Required dryv-cli architecture

`dryv_cli` must be folder-based with: `app/`, `commands/`, `project/`, `resolvers/`, `connections/api/`, `connections/author/`, `local/`, `generation/`, `artifacts/`, `filesystem/`, and `presentation/`.

The CLI is the reference Project Client and local process orchestrator. Stream and ZIP delivery must normalize into the same verified artifact model before filesystem diff/apply. Local process plumbing is hidden from the user.

## Task order

- HELPER-01 Author architecture cleanup
- HELPER-02 Author core registry, refs, naming, metadata
- HELPER-03 Properties, schemas, projections, types
- HELPER-04 Failures, events, operations
- HELPER-05 Storage, value sources, policies
- HELPER-06 Workflows, views, presentations
- HELPER-07 Groups, ownership and composition
- HELPER-08 Compiler context and deterministic pipeline
- HELPER-09 Author loading and host boundary
- **STOP: AUTHOR PRODUCTION-CODE REVIEW**
- HELPER-10 Rewrite Jinja Render Client
- HELPER-11 CLI project and resolvers
- HELPER-12 CLI Author/API connections
- HELPER-13 CLI temporary local environment
- HELPER-14 CLI generation workflow
- HELPER-15 CLI artifact stream/bundle handling
- HELPER-16 CLI filesystem diff/stage/apply
- HELPER-17 CLI presentation and final commands
- **STOP: ALL PRODUCTION-CODE REVIEW**
- Tests may be planned only after explicit approval of this final review gate.

A task may not be marked DONE merely because files exist. Its completion checklist and boundary rules must be satisfied by real production code.