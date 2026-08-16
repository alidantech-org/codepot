# HELPER-14 — CLI generation workflow

Status: TODO
Prerequisite: HELPER-13 DONE.

## Goal
Compose project resolution, optional author compilation, API planning, renderer availability, preflight and rendering into one inspectable CLI workflow.

## Required structure
Implement `generation/request.py`, `build.py`, `plan.py`, and `progress.py`.

Required flow:

```text
discover project
→ obtain/compile Canonical IR
→ collect dryv.yaml + pack/resource bundles
→ connect/start API
→ submit build inputs
→ receive GenerationPlan
→ determine required renderer capabilities from plan/API
→ ensure local renderers when needed
→ preflight
→ render
→ expose ordered progress/events/artifact delivery
```

`plan` must be usable without writing generated files. `generate` uses the same planning/build path rather than a second shortcut implementation.

## Enforcement
Never synthesize selectors, template contexts, output paths, dependencies or job order in CLI; Runtime/GenerationPlan is authoritative. Do not bypass API by importing internal Runtime execution for convenience. No filesystem application here.

## Completion
One production workflow drives local or remote dryv-api consistently and reports failures/progress without semantic duplication. No tests yet.