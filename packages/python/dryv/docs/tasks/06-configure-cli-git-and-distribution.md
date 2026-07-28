# Configure, CLI, Git, and distribution tasks

## SETUP-001 — Typed configure questions

- [ ] Define typed question, candidate, answer, validation, and update-result models.
- [ ] Generate questions from project/provider configuration, pack options, bindings, executable defaults, and command approvals.
- [ ] Support text, path, typed values, discovered binding candidates, and approvals.
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
- [ ] Resolve identity and show trust/command requirements before configuration.
- [ ] Suggest a unique project-local instance name.
- [ ] Update the lock only after successful resolution.
- [ ] Never create a registry alias or `use` indirection.

## CONFIGURE-003 — Contract-provider setup

- [ ] Configure canonical IR files.
- [ ] Configure Python module/callable providers.
- [ ] Validate imported callable results as public Dryv contracts.
- [ ] Report missing modules, callables, wrong return types, and contract validation failures safely.
- [ ] Allow hosts to inject in-memory contracts without project-file serialization.

## DRYV-CLI-001 — Standalone package

- [ ] Create `packages/python/dryv-cli` and `src/dryv_cli`.
- [ ] Depend on `dryv`, never the reverse.
- [ ] Register `dryv = dryv_cli.main:main`.
- [ ] Move current argument parsing and JSON terminal output out of the runtime distribution.
- [ ] Preserve runtime-only installation and imports.

## DRYV-CLI-002 — Initial commands

```text
dryv validate project
dryv validate pack
dryv validate plugin
dryv plugins list
dryv plugins inspect
dryv plan
dryv generate
dryv ir emit
dryv state inspect
```

- [ ] Parse arguments into typed public runtime requests.
- [ ] Render structured diagnostics and results.
- [ ] Define stable exit codes.
- [ ] Keep all business logic out of command handlers.

## MCP-001 — Structured adapter surface

- [ ] Ensure runtime requests/results serialize without terminal-only fields.
- [ ] Expose validate, inspect, plan, generate-memory/archive, pack, provider, lock, and approval operations.
- [ ] Apply server-safe policy by default.
- [ ] Support progress and cancellation hooks.

## GIT-001 — Local pack provider

- [ ] Resolve `source.local` relative to `dryv.yaml`.
- [ ] Validate containment, manifest, identity/version, and digest.
- [ ] Create a stable run snapshot so mid-run edits cannot change a plan.
- [ ] Detect local content drift against frozen locks.
- [ ] Never execute pack commands during resolution.

## GIT-002 — Generic Git provider

- [ ] Resolve HTTPS/SSH URLs, required refs, and optional subdirectories.
- [ ] Use existing Git credentials, SSH agents, and credential helpers.
- [ ] Resolve branches/tags/commits to immutable commits.
- [ ] Fetch into a controlled content-addressed cache and clean partial failures.
- [ ] Validate repository-relative containment and pack identity.
- [ ] Redact credentials from diagnostics and events.
- [ ] Support public, private, and enterprise hosts through one provider.

No host-specific locator is required; every service is treated as an ordinary Git host.

## GIT-003 — Source and discovery integration

- [ ] Enforce exactly one of `source.local` or `source.git`.
- [ ] Require `ref` for Git sources.
- [ ] Keep pack identity/version in the resolved manifest.
- [ ] Let future discovery tools return complete source blocks without becoming runtime registries.
- [ ] Add local, Git-root, monorepo, branch, tag, commit, SSH, and invalid-source fixtures.

## LOCK-001 — `dryv.lock.yaml`

- [ ] Define typed `dryv.dev/lock/v1` models.
- [ ] Record project/runtime behavior identity.
- [ ] Record requested local/Git source identity.
- [ ] Record exact commits, pack IDs/versions, manifest/content digests, plugin versions, and behavior versions.
- [ ] Keep credentials, secrets, environment values, approval tokens, and generated output hashes out of the lock.
- [ ] Implement deterministic serialization.

## LOCK-002 — Reproducibility and approvals

- [ ] Include lock identity in generation and cache keys.
- [ ] Tie command approvals to exact source, commit, path, digests, executable, and arguments.
- [ ] Require reapproval after any relevant change.
- [ ] Implement inspect, update, frozen, and offline checks.
- [ ] Never update a frozen lock silently.

## DIST-001 — Runtime distribution

- [ ] Publish `dryv` with no mandatory CLI, authoring, target, engine, or pack defaults.
- [ ] Prove embedded hosts can install only required plugins.
- [ ] Document executable Python-plugin trust.

## DIST-002 — Interface and official plugins

- [ ] Publish `dryv-cli`, `dryv-author`, `dryv-template-jinja`, `dryv-language-typescript`, and `dryv-language-dart` independently.
- [ ] Pin compatible public runtime ranges.
- [ ] Test runtime-only and full development installations.
- [ ] Verify fresh-wheel entry points and connected generation.

## DIST-003 — Pack discovery metadata

- [ ] Define marketplace metadata: ID, description, Git URL, suggested refs, pack path, targets, frameworks, bindings, commands, docs, and verification.
- [ ] Return a complete `source` block suitable for `dryv.yaml`.
- [ ] Keep runtime resolution direct from the project source block.
- [ ] Keep private packs as direct unindexed references.

## Acceptance gate

- Local and Git examples decode exactly.
- Git refs resolve to immutable commits.
- Lock output is deterministic and credential-free.
- No registry aliases, host-specific shorthand, or mutable catalog mapping are required.
- Runtime operations execute no commands or network work unless the host permits them.
- `dryv` works without `dryv-cli` installed.
- The full package family installs from real wheels and resolves each plugin exactly once.
