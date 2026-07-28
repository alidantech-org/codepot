# Configure, CLI, Git, and distribution tasks

## SETUP-001 — Typed configure question model

**Status:** planned

**Dependencies:** CFG schema introspection, PACKCFG-003, BIND-002

- [ ] Define typed question, candidate, answer, validation, and update result models.
- [ ] Generate questions from pack options, bindings, executable defaults, and command approvals.
- [ ] Support typed text/path/value, discovered binding candidate, and approval prompts.
- [ ] Keep the workflow frontend-neutral.

## CONFIGURE-001 — Configure project workflow

**Status:** planned

**Dependencies:** SETUP-001, API facade, pack provider

- [ ] Load and validate `dryv.yaml`.
- [ ] Resolve each direct `packs.<instance>.source` and read `DryvPack.yaml`.
- [ ] Ask only for missing or invalid public pack inputs, bindings, executable choices, and approvals.
- [ ] Write project answers directly under the matching pack instance.
- [ ] Preserve unrelated project configuration/comments where practical.
- [ ] Support configure all, one pack, and non-interactive `--check`.

## CONFIGURE-002 — Add-pack workflow

**Status:** planned

**Dependencies:** CONFIGURE-001, GIT-001, GIT-002

- [ ] Add a local pack with `source.local`.
- [ ] Add a Git pack with `source.git`, required `ref`, and optional `path`.
- [ ] Resolve identity and show trust/command requirements before configuring.
- [ ] Suggest a unique project-local instance name.
- [ ] Update the lock only after successful resolution.
- [ ] Do not create a registry alias or `use` indirection.

## CONFIGURE-003 — Detection and readiness report

**Status:** planned

**Dependencies:** CONFIGURE-001, ecosystem/language adapters

- [ ] Detect candidate source files, executable names/paths, bindings, and project units.
- [ ] Never silently choose ambiguous binding candidates.
- [ ] Report remaining bindings, executable replacements, command approvals, and manual work.
- [ ] Support flexible local and strict CI checks.

## CLI-001 — Thin CLI shell

**Status:** planned

**Dependencies:** public API operations

- [ ] Implement configure, validate, plan, generate, plugins, pack inspect/add, lock, approvals, and cache commands.
- [ ] Parse arguments into typed API requests.
- [ ] Render structured diagnostics/events/results.
- [ ] Define stable exit-code policy.
- [ ] Keep generation/configuration business logic out of handlers.

## MCP-001 — Structured adapter surface

**Status:** planned

**Dependencies:** API-002

- [ ] Ensure requests/results serialize without terminal-only fields.
- [ ] Define validate, inspect plan, generate memory/archive, inspect pack, configure, lock, and approval operations.
- [ ] Apply server-safe policy by default.
- [ ] Support progress/cancellation hooks.

## GIT-001 — Local pack provider

**Status:** planned

**Dependencies:** pack-provider port, PACKCFG loader

- [ ] Resolve `source.local` relative to `dryv.yaml`.
- [ ] Validate containment, manifest presence, identity/version, and content digest.
- [ ] Create a stable run snapshot so mid-run edits cannot change the plan.
- [ ] Detect local content drift against frozen locks.
- [ ] Never execute pack commands during source resolution.

## GIT-002 — Generic Git provider

**Status:** planned

**Dependencies:** GIT-001, controlled Git/process infrastructure

- [ ] Resolve `source.git` HTTPS/SSH URL, required `ref`, and optional subdirectory.
- [ ] Use existing Git credentials, SSH agents, and credential helpers.
- [ ] Resolve branch/tag/commit to one immutable commit.
- [ ] Fetch into a controlled content-addressed cache and clean partial failures.
- [ ] Validate repository-relative `path` containment and pack identity.
- [ ] Redact credentials from diagnostics/events.
- [ ] Support public, private, and enterprise Git hosts through the same provider.

**Acceptance:** no GitHub-specific locator is required; GitHub is handled as a normal Git host.

## GIT-003 — Source syntax and discovery integration

**Status:** planned

**Dependencies:** GIT-001, GIT-002, CONFIGURE-002

- [ ] Enforce exactly one of `source.local` or `source.git`.
- [ ] Require `ref` for every Git source.
- [ ] Keep pack identity/version in the resolved manifest rather than project config.
- [ ] Allow a future marketplace to return complete source blocks without becoming a runtime registry.
- [ ] Add local, Git-root, Git-monorepo, branch, tag, commit, SSH, and invalid-source fixtures.

## LOCK-001 — `dryv.lock.yaml` schema and resolver

**Status:** planned

**Dependencies:** version/digest primitives, GIT providers, plugin registry

- [ ] Define typed `dryv.dev/lock/v1` schema.
- [ ] Record project/runtime behavior identity.
- [ ] Record each instance's requested local path or Git URL/ref/path.
- [ ] Record exact Git commit, discovered pack ID/version, manifest/content digests, plugin versions, and behavior versions.
- [ ] Keep local content digests for frozen drift detection.
- [ ] Never store credentials, secrets, environment values, or approval tokens.
- [ ] Implement deterministic serialization matching the checked-in example.

## LOCK-002 — Reproducibility and approvals

**Status:** planned

**Dependencies:** LOCK-001, CMD approval infrastructure

- [ ] Include lock identity in generation/cache keys.
- [ ] Tie pack command approvals to exact source, commit, subdirectory, digest, executable reference, and arguments.
- [ ] Require reapproval on source/content/command change.
- [ ] Implement inspect, update, frozen, and offline checks.
- [ ] Never update a frozen lock silently.

## DIST-001 — Minimal core distribution

**Status:** planned

**Dependencies:** stable core/plugin contracts

- [ ] Publish `dryv` with no mandatory source/language/engine/pack defaults.
- [ ] Prove embedded hosts can choose only required plugins.
- [ ] Document executable Python-plugin trust.

## DIST-002 — Batteries-included distribution

**Status:** planned

**Dependencies:** official adapter/pack releases

- [ ] Publish `dryv` as the simple user installation.
- [ ] Depend on compatible OpenAPI, TypeScript, Dart, Jinja, and initial SDK packs.
- [ ] Expose the CLI entry point.
- [ ] Test fresh installation and immediate plugin listing/generation.

## DIST-003 — Optional pack discovery metadata

**Status:** planned

**Dependencies:** direct Git source identity stable

- [ ] Define metadata a future website may index: ID, description, Git URL, ref/tag suggestions, pack path, targets, frameworks, bindings, commands, docs, and verification.
- [ ] Make discovery return a complete `source` block suitable for insertion into `dryv.yaml`.
- [ ] Keep runtime pack resolution direct from the project source block.
- [ ] Ensure private packs remain direct unindexed references.

## Acceptance gate

- Local and Git project examples decode exactly.
- Git refs resolve to immutable commits.
- The mixed example produces a deterministic `dryv.lock.yaml` shape.
- No `registries`, `use`, GitHub shorthand, or mutable catalog mapping is required.
- Existing Git credentials work without being persisted.
- Server-safe structured operations execute no commands or network resolution unless the host permits them.
- Batteries-included installation works without manual adapter setup.
