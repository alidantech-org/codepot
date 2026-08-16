# HELPER-14 — CLI generation workflow

Status: DONE — PRODUCTION REVIEWED
Prerequisite: HELPER-13 DONE.

## Implemented flow
The CLI has one shared generation workflow:

```text
discover/resolve inputs
→ optional Author compile
→ create API build
→ Runtime GenerationPlan
→ inspect required renderer capabilities
→ ensure owned local renderers when applicable
→ API template preflight
→ API render execution
```

`PlannedBuild` is the stable handoff for `dryv plan`; `generate` advances that same build through preflight/render rather than using another code path. The workflow only reads GenerationPlan renderer/artifact metadata and never derives selectors, contexts, paths, dependencies or ordering.

Build request IDs are unique execution identities; Dryv plan hashing excludes buildId so semantic plan reproducibility is preserved.

## Review hardening
Failed planning states are released, unexpected non-terminal states are cancelled/released, API build IDs are route-safe, preflight waits cancellably for transient renderer capacity, and render scheduling queues when compatible slots are temporarily occupied instead of turning server load into a false generation failure.

## Completion
Planning and rendering orchestration are connected through public Author/API boundaries with no filesystem application in this module. Production source was reviewed; executable test certification remains separate.
