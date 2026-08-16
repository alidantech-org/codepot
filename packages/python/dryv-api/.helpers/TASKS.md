# Dryv helper rewrite tasks

Status: PRODUCTION IMPLEMENTATION AND REVIEW COMPLETE — EXECUTABLE CERTIFICATION PENDING
Branch: `develop` only
Scope: `packages/python/dryv-api/.helpers/{dryv-author,dryv-template-jinja,dryv-cli}`

The approved HELPER-01 through HELPER-17 production sequence and the mandatory architecture/integration review are complete. This does **not** claim executable test certification; the root lockfile still predates helper relocation and must be regenerated in a dependency-resolving environment before frozen workspace certification.

## Non-negotiable architecture

```text
Authoring source
    ↓
dryv-author
    ↓
Canonical Dryv Runtime IR
    ↓
dryv-cli collects dryv.yaml + IR + resolved local/Git pack bundles
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

- HELPER-01 through HELPER-09: Author rewrite and production review
- HELPER-10: renderer-neutral Jinja client and production review
- HELPER-11: CLI project/resolvers and local/Git pack resolution
- HELPER-12: Author/API connections
- HELPER-13: temporary local API/renderer environment
- HELPER-14: shared plan/render workflow
- HELPER-15: stream/bundle artifact normalization
- HELPER-16: filesystem diff/stage/apply
- HELPER-17: final commands/presentation and old CLI removal

## Review hardening completed

The review corrected Author target/navigation validation, Author subprocess bounds/protocol strictness, Jinja media types/context-path validation/concurrency/failure propagation, ASGI event-loop blocking, renderer preflight and render-capacity queuing, renderer protocol size/hash/lifecycle checks, Git pack acquisition, strict project/wire decoding, route-safe build identities, stream/ZIP provenance verification, reserved `.dryv` outputs, symlink conflicts, and filesystem diff→apply race protection.

## Remaining certification work

- Regenerate `uv.lock` after the relocated helper workspace packages are resolved.
- Run import/package/CLI and end-to-end stream + bundle certification in an environment with repository/dependency access.
- Do not describe the production path as test-certified until those commands actually pass.
