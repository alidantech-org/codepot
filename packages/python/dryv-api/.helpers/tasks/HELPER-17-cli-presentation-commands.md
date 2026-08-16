# HELPER-17 — CLI presentation and final commands

Status: DONE — PRODUCTION REVIEWED
Prerequisite: HELPER-16 DONE.
Review gate: production architecture/integration review completed.

## Implemented public experience
- `dryv validate` compiles Author source when required, submits the resulting Canonical IR through dryv-api/Runtime validation/planning, reports diagnostics and performs no generated-file writes.
- `dryv compile` invokes the Author host and emits Canonical JSON/JSONL/YAML to stdout or an explicit project-relative file.
- `dryv plan` uses the same API planning path and prints a summary or canonical plan JSON without rendering/applying files.
- `dryv generate` advances that planned build through renderer availability, preflight, rendering, verified stream/bundle normalization, local diff and safe apply.

The old flat CLI, stdio API transport, monolithic Project Client, generic services/prompts and superseded presentation modules are removed rather than wrapped.

## Production review result
The connected production path has been reviewed and hardened across Author process boundaries, HTTP/ASGI coordination, renderer registration/capacity/cancellation, Jinja context preflight, stream and ZIP provenance verification, and local filesystem race/conflict safety. No compatibility path was restored.

## Certification boundary
This task is production-reviewed, not executable-test certified. The current environment could not clone the repository because external DNS is unavailable, and the relocated workspace still requires a regenerated `uv.lock` in a dependency-resolving environment before frozen workspace certification can be claimed.
