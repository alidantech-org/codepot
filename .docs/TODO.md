# Current work

Dryv's approved production architecture is implemented through the Engine, `dryv-api`, Python Author helper, Jinja Render Client, and reference CLI Project Client.

```text
Authoring source
    ↓
dryv-author
    ↓
Canonical Dryv Runtime IR
    ↓
dryv-cli collects dryv.yaml + IR + resolved pack bundles
    ↓
dryv-api
    ↓
Dryv Runtime → GenerationPlan
    ↓
dryv-api preflight/scheduling
    ↓
Render Client(s)
    ↓
streamed artifacts or deterministic ZIP
    ↓
dryv-cli verify/diff/stage/apply
    ↓
local filesystem
```

## Production implementation status

- [x] Dryv Engine boundary cleanup
- [x] Canonical `GenerationPlan` Runtime
- [x] dryv-api build/resource coordination
- [x] renderer-neutral protocol and preflight
- [x] dependency-aware bounded render scheduling
- [x] HTTP/WebSocket transport and artifact delivery
- [x] deterministic ZIP bundle delivery
- [x] rich Python `dryv-author` compiler
- [x] Jinja Render Client
- [x] CLI project/resource resolvers
- [x] local and Git Template Pack resolution using normal Git credentials
- [x] CLI Author/API connections
- [x] temporary loopback API and local renderer orchestration
- [x] shared plan/generate workflow
- [x] stream/bundle artifact verification
- [x] local conflict detection, staging and atomic apply
- [x] public `dryv validate`, `dryv compile`, `dryv plan`, `dryv generate` commands
- [x] production architecture/bug review and hardening

## Current review notes

The production review fixed renderer lifecycle/protocol edge cases, deterministic bundle path collisions, premature build release, Jinja template media-type detection, Windows Author targets, presentation navigation validation, strict duplicate-key handling, route-safe build IDs, failed remote-build cleanup, reserved `.dryv` output paths, and Git-backed packs.

## Remaining certification work

The production code is ready for executable certification, but the previously approved no-test gate has not been lifted. No test suite has been added or run as part of the architecture work.

The root uv workspace now includes the relocated helper packages. `uv.lock` was produced before that relocation and must be regenerated once executable/testing work is explicitly approved and a dependency-resolving environment is available.

## Rules retained

- `develop` only; never create a work branch for this project.
- no compatibility shims or old/new dual architecture;
- Canonical Runtime IR remains the only semantic authority;
- Runtime stops at `GenerationPlan`;
- API owns renderer topology/execution/delivery;
- Render Clients do not interpret Dryv semantics;
- CLI/Project Client is the only generated-project filesystem writer;
- keep production modules focused and around/under 500 lines.
