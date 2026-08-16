# HELPER-14 — CLI generation workflow

Status: DONE
Prerequisite: HELPER-13 DONE.

## Implemented flow
The CLI now has one shared generation workflow:

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

Build request IDs are unique execution identities; Dryv plan hashing now excludes buildId so semantic plan reproducibility is preserved.

## Completion
Planning and rendering orchestration are connected through public Author/API boundaries with no filesystem application in this module. No tests were added or run.
