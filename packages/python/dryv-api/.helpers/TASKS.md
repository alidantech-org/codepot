# Dryv helper rewrite tasks

Status: PRODUCTION IMPLEMENTATION COMPLETE — REVIEW REQUIRED
Branch: `develop` only
Scope: `packages/python/dryv-api/.helpers/{dryv-author,dryv-template-jinja,dryv-cli}`

The approved helper implementation sequence HELPER-01 through HELPER-17 is complete in production code. The mandatory next action is production-code architecture/integration review. **Do not add, modify, delete, regenerate or run tests until explicit approval starts the testing phase.**

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

## Enforcement retained after implementation

1. Work directly on `develop`. Never create a branch.
2. Existing/deprecated code is reference material only; no compatibility shims or old/new dual modes.
3. Production files remain focused and target <=500 lines; no generic dumping-ground modules.
4. Authoring defines software meaning and compiles to Canonical IR; it does not generate application source or understand packs/renderers/output paths.
5. Runtime IR is the semantic authority. Runtime owns config/IR/pack meaning and deterministic GenerationPlan construction.
6. dryv-api owns transport, renderer discovery, preflight, scheduling and delivery.
7. Render Clients understand template engine syntax plus supplied context only.
8. CLI resolvers answer where inputs come from; they do not interpret semantic generation meaning.
9. `dryv_cli/filesystem` is the only helper owner of generated project-file mutation.
10. Preserve deterministic hashes, explicit references, diagnostics, bounded streams, verified bytes, safe paths and explicit conflict handling.

## Completed sequence

- HELPER-01 through HELPER-09: Author rewrite and review corrections
- HELPER-10: renderer-neutral Jinja client
- HELPER-11: CLI project/resolvers
- HELPER-12: Author/API connections
- HELPER-13: temporary local API/renderer environment
- HELPER-14: shared plan/render workflow
- HELPER-15: stream/bundle artifact normalization
- HELPER-16: filesystem diff/stage/apply
- HELPER-17: final commands/presentation and old CLI removal

## Mandatory review gate

Review the production architecture and actual connections end-to-end. Tests remain deferred until the user explicitly approves this review gate.
