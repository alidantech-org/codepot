# HELPER-17 — CLI presentation and final commands

Status: DONE — PRODUCTION REVIEW REQUIRED
Prerequisite: HELPER-16 DONE.
Review gate: ALL PRODUCTION-CODE REVIEW after completion.

## Implemented public experience
- `dryv validate` compiles Author source when required, submits the resulting Canonical IR through dryv-api/Runtime validation/planning, reports diagnostics and performs no generated-file writes.
- `dryv compile` invokes the Author host and emits Canonical JSON/JSONL/YAML to stdout or an explicit project-relative file.
- `dryv plan` uses the same API planning path and prints a summary or canonical plan JSON without rendering/applying files.
- `dryv generate` advances that planned build through renderer availability, preflight, rendering, verified stream/bundle normalization, local diff and safe apply.

The old flat CLI, stdio API transport, monolithic Project Client, generic services/prompts and superseded presentation modules are removed rather than wrapped.

## Mandatory stop
Production implementation through HELPER-17 is complete. Perform architecture/integration review only now. Do not add, modify, delete, regenerate or run tests until explicit approval starts the testing phase.
