# Current work

Dryv's approved production architecture is implemented and production-reviewed through the Engine, `dryv-api`, Python Author helper, Jinja Render Client, and reference CLI Project Client.

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

## Production review fixes

The review hardened:

- Author target parsing on Windows and presentation navigation ownership/cycles;
- Author subprocess timeout, strict host-envelope validation and exit-status agreement;
- Jinja template media types, empty/nested context-contract validation, advertised concurrency and worker/sender failure propagation;
- ASGI planning/preflight execution so blocking Runtime/renderer work cannot deadlock renderer WebSockets;
- renderer fingerprint preflight, cancellable transient-capacity waiting, render-capacity queuing, declared-size/hash/protocol lifecycle checks, duplicate-registration cleanup and closed-state propagation;
- strict project/API duplicate/unknown-field decoding and route-safe build identities;
- local and Git pack acquisition through normal Git configuration/credentials;
- streamed artifact job/order/dependency provenance and deterministic ZIP semantic provenance;
- reserved `.dryv` outputs and symlink conflicts;
- diff→apply time-of-check/time-of-use protection, managed-state rechecks, final-byte verification and failed-state-temp cleanup;
- pack `requires` / `executables` / `commands` declarations now fail explicitly instead of being silently ignored until a typed planned-execution contract is implemented.

No old AuthorSession/RenderSession/stdio compatibility path was restored.

## Remaining certification work

Production review is complete, but executable certification is not.

- The root uv workspace includes the relocated helper packages, but `uv.lock` was produced before that relocation and must be regenerated in a dependency-resolving environment.
- The current assistant execution environment cannot clone GitHub because external DNS resolution is unavailable, so no repository checkout/test execution was falsely claimed.
- After lock regeneration, run package/import/CLI checks and real `dryv validate → compile → plan → generate` samples for both `stream` and `bundle` delivery before calling the stack test-certified.

## Rules retained

- `develop` only; never create a work branch for this project.
- no compatibility shims or old/new dual architecture;
- Canonical Runtime IR remains the only semantic authority;
- Runtime stops at `GenerationPlan`;
- API owns renderer topology/execution/delivery;
- Render Clients do not interpret Dryv semantics;
- CLI/Project Client is the only generated-project filesystem writer;
- keep production modules focused and around/under 500 lines.
