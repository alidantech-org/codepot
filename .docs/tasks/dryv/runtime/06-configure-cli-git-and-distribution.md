# Configure, CLI, Git, and distribution tasks

## SETUP-001 — Typed configure questions

- [ ] Define typed question, candidate, answer, validation, and update-result models.
- [ ] Generate questions from project/provider configuration, pack options, bindings, executable defaults, and command approvals.
- [ ] Keep the workflow independent from CLI, IDE, web, or server presentation.

## CONFIGURE-001 — Project workflow

- [ ] Load and validate `dryv.yaml` through `DryvRuntime`.
- [ ] Resolve contract providers and pack sources.
- [ ] Ask only for missing or invalid public inputs, bindings, executables, and approvals.
- [ ] Preserve unrelated configuration and comments where practical.
- [ ] Support all packs, one pack, and non-interactive check modes.

## CONFIGURE-002 — Add-pack workflow

- [ ] Add local packs through `source.local`.
- [ ] Add Git packs through `source.git`, required `ref`, and optional `path`.
- [ ] Resolve identity and trust/command requirements before configuration.
- [ ] Update the lock only after successful resolution.
- [ ] Never create a registry alias or `use` indirection.

## CONFIGURE-003 — Contract-provider setup

- [ ] Configure canonical IR files.
- [ ] Configure Python module/callable providers.
- [ ] Validate callable results as public Dryv contracts.
- [ ] Report import/call/type/contract failures safely.
- [ ] Allow hosts to inject in-memory contracts without serialization.

## DRYV-CLI-001 — Standalone package

**Status:** implemented; verification required

- [x] Create `packages/python/dryv-cli` and `src/dryv_cli`.
- [x] Depend on `dryv`, never the reverse.
- [x] Register `dryv = "dryv_cli.main:main"`.
- [x] Remove the embedded core CLI and core console script.
- [x] Preserve runtime-only installation and imports.
- [x] Add package architecture and distribution tests.
- [x] Remove stale `.gitkeep` from implemented runtime and test directories.

## DRYV-CLI-002 — Initial command foundation

**Status:** implemented for public runtime operations; expansion blocked on runtime APIs

Implemented:

```text
dryv
├── plan
├── generate
└── plugins
```

- [x] Parse commands with Click.
- [x] Use Rich for all terminal output, colors, trees, summaries, and spinners.
- [x] Use Questionary for interactive confirmation.
- [x] Define stable operation exit codes.
- [x] Support plain `--json` machine output.
- [x] Keep command handlers free of business logic.
- [x] Prohibit Python `print()` and `input()`.
- [x] Prohibit Rich panels and box-border layouts.
- [x] Prevent prompts in JSON and non-interactive automation.

Blocked until matching public runtime operations exist:

```text
dryv validate project
dryv validate pack
dryv validate plugin
dryv plugins inspect
dryv ir emit
dryv state inspect
```

## DRYV-CLI-003 — UX and accessibility hardening

- [x] Borderless root command tree.
- [x] Hierarchical artifact, diagnostic, plugin, and write trees.
- [x] Shared semantic color theme.
- [x] Loading indicators for runtime discovery, planning, and generation.
- [x] TTY-aware confirmation with `--yes` automation escape.
- [x] Regression tests for no panels/boxes and no ANSI in JSON.
- [ ] Add terminal-width snapshots for narrow and wide consoles.
- [ ] Add `NO_COLOR` and accessibility review evidence.
- [ ] Add shell completion after the command surface stabilizes.

## MCP-001 — Structured adapter surface

- [ ] Ensure runtime requests/results serialize without terminal-only fields.
- [ ] Expose validate, inspect, plan, generation, provider, lock, and approval operations.
- [ ] Apply server-safe policy by default.
- [ ] Support progress and cancellation hooks.

## GIT-001 — Local pack provider

- [ ] Resolve `source.local` relative to `dryv.yaml`.
- [ ] Validate containment, manifest, identity/version, and digest.
- [ ] Create stable run snapshots and detect lock drift.
- [ ] Never execute pack commands during resolution.

## GIT-002 — Generic Git provider

- [ ] Resolve HTTPS/SSH URLs, refs, and optional subdirectories.
- [ ] Use existing Git credentials and helpers.
- [ ] Resolve mutable refs to immutable commits.
- [ ] Use controlled caches and clean partial failures.
- [ ] Validate containment and redact credentials.

No host-specific locator is required.

## LOCK-001 — `dryv.lock.yaml`

- [ ] Define typed `dryv.dev/lock/v1` models.
- [ ] Record runtime behavior, source identity, exact commits, pack/plugin versions, and digests.
- [ ] Exclude credentials, secrets, approvals, and generated output hashes.
- [ ] Implement deterministic serialization.

## DIST-001 — Runtime distribution

**Status:** implementation boundary complete; wheel verification required

- [x] `dryv` declares no console script.
- [x] `dryv` declares no CLI/TUI dependency.
- [x] `dryv` exposes `DryvRuntime`, `create_runtime`, and runtime inspection models.
- [ ] Build and inspect the real runtime wheel.
- [ ] Prove runtime-only installation in a fresh environment.

## DIST-002 — Interface and official plugins

**Status:** `dryv-cli` implementation present; family verification required

- [x] Add independent `dryv-cli` distribution metadata.
- [x] Pin a compatible public runtime range.
- [x] Add console-script ownership tests.
- [ ] Build and inspect the real CLI wheel.
- [ ] Install runtime and CLI wheels together in a fresh environment.
- [ ] Verify all official plugin wheels and connected generation.

## DIST-003 — Pack discovery metadata

- [ ] Define marketplace metadata and complete source blocks.
- [ ] Keep runtime resolution direct and private packs unindexed.

## Acceptance gate

- `dryv` imports and operates without `dryv-cli`.
- `dryv-cli` owns the only new `dryv` console script.
- Runtime and CLI lint, formatting, tests, builds, and wheel inspection pass.
- CLI help/results remain borderless and readable.
- JSON remains plain and non-interactive.
- Full package-family wheels resolve every plugin exactly once.
- Git, lock, and configure claims remain blocked until their implementations exist.
