# Configure, CLI, Git, and distribution tasks

## SETUP-001 — Typed configure question model

**Status:** planned

**Dependencies:** CFG schema introspection, PACKCFG-003, BIND-002

- [ ] Define typed question, candidate, answer, validation, and update result models.
- [ ] Generate questions from pack option/binding/setup descriptors rather than hardcoded CLI flows.
- [ ] Support single choice, multiple choice, boolean, typed text/path/value, discovered import candidate, and approval prompt.
- [ ] Keep the application workflow frontend-neutral.

## CONFIGURE-001 — Configure project workflow

**Status:** planned

**Dependencies:** SETUP-001, API facade, pack provider

- [ ] Load and validate `codepotg.yaml`.
- [ ] Resolve all selected packs and read `CodepotgPack.yaml`.
- [ ] Inspect project units, manifests, lockfiles, aliases, and declared discovery locations through controlled ports.
- [ ] Ask only for missing or invalid public pack inputs.
- [ ] Write results directly under `packs.<instance>` in `codepotg.yaml`.
- [ ] Preserve unrelated project configuration/comments where practical.
- [ ] Support configure all, one pack instance, and non-interactive `--check`.

## CONFIGURE-002 — Add-pack workflow

**Status:** planned

**Dependencies:** CONFIGURE-001, GIT/local provider

- [ ] Implement add local/Git/GitHub pack as a named instance.
- [ ] Resolve identity and show trust/command requirements before configuring.
- [ ] Suggest a unique instance name.
- [ ] Run pack setup questions after adding.
- [ ] Update lock only after successful resolution.

## CONFIGURE-003 — Detection and readiness report

**Status:** planned

**Dependencies:** CONFIGURE-001, ecosystem adapters

- [ ] Detect package managers, project units, manifests, candidate symbols/files/modules, and likely framework capabilities.
- [ ] Never silently choose ambiguous binding candidates.
- [ ] Produce remaining dependency, binding, command approval, and manual-step report.
- [ ] Support flexible local and strict CI checks.

## CLI-001 — Thin CLI shell

**Status:** planned

**Dependencies:** public API operations

- [ ] Implement commands: configure, validate, plan, generate, plugins, pack inspect/add, lock, approvals, cache.
- [ ] Parse arguments into typed API requests.
- [ ] Render structured diagnostics/events/results.
- [ ] Define stable exit-code policy.
- [ ] Keep generation/configuration business logic out of handlers.
- [ ] Test CLI/API result equivalence.

## MCP-001 — Structured adapter surface

**Status:** planned

**Dependencies:** API-002

- [ ] Ensure requests/results serialize without terminal-specific fields.
- [ ] Define tool-ready operations for validate, inspect plan, generate memory/archive, list plugins, inspect pack, configure questions, and approvals.
- [ ] Apply server-safe policy by default.
- [ ] Support progress/cancellation hooks.

## GIT-001 — Local pack provider

**Status:** planned

**Dependencies:** pack-provider port, PACKCFG loader

- [ ] Resolve local directory and optional subdirectory.
- [ ] Validate containment, manifest presence, content digest, and trust metadata.
- [ ] Snapshot or otherwise prevent mid-run mutation from producing inconsistent plans.

## GIT-002 — Generic Git provider

**Status:** planned

**Dependencies:** GIT-001, safe command/process infrastructure or Git library decision

- [ ] Resolve HTTPS/SSH repository, ref, and pack subdirectory.
- [ ] Use existing Git credentials/credential helpers.
- [ ] Resolve branch/tag to immutable commit.
- [ ] Fetch into controlled cache and clean partial failures.
- [ ] Redact credentials from diagnostics/events.
- [ ] Support private repositories without storing tokens in project/lock files.

## GIT-003 — GitHub shorthand

**Status:** planned

**Dependencies:** GIT-002

- [ ] Resolve `owner/repository` shorthand to a Git URL.
- [ ] Support optional ref and subdirectory.
- [ ] Keep provider implementation generic enough for GitHub Enterprise and other Git hosts later.

## LOCK-001 — Lock schema and resolver

**Status:** planned

**Dependencies:** version/digest primitives, GIT providers, plugin registry

- [ ] Define typed `codepotg.lock` schema.
- [ ] Record requested locator/ref, resolved commit/version, subdirectory, manifest/content digest, plugin versions, behavior versions, IR/schema versions, and selected profile.
- [ ] Implement locked and latest-compatible resolution modes.
- [ ] Report drift and missing/incompatible locked components.
- [ ] Never store credentials/secrets.

## LOCK-002 — Reproducibility and approvals

**Status:** planned

**Dependencies:** LOCK-001, CMD-003

- [ ] Include lock identity in generation result/cache keys.
- [ ] Tie pack command approvals to exact locked identity.
- [ ] Require reapproval on commit/digest change.
- [ ] Add lock inspect/update/frozen checks.

## DIST-001 — Minimal core distribution

**Status:** planned

**Dependencies:** stable core/plugin contracts

- [ ] Publish metadata for `codepotg-core` with no mandatory source/language/engine/pack defaults.
- [ ] Prove embedded hosts can choose only required plugins.
- [ ] Document executable Python-plugin trust.

## DIST-002 — Batteries-included distribution

**Status:** planned

**Dependencies:** official adapter/pack releases

- [ ] Publish `codepotg` as the simple user installation.
- [ ] Depend on compatible OpenAPI, TypeScript, Dart, Jinja, and default SDK packs.
- [ ] Expose the CLI entry point.
- [ ] Add extras for optional future adapters.
- [ ] Test `pip install codepotg` in a fresh environment and immediate plugin listing/generation.

## DIST-003 — Pack discovery metadata

**Status:** planned

**Dependencies:** Git pack identity stable

- [ ] Define metadata the future website can index: ID, description, Git repository, pack path, tags, versions, targets, frameworks, dependencies, bindings, commands, docs, verification.
- [ ] Keep initial installation from Git rather than requiring hosted pack bytes.
- [ ] Ensure private packs can remain direct project Git references.

## Acceptance gate

- Configure writes only `codepotg.yaml` for project-owned answers.
- CLI is a frontend over Python API.
- Git providers use existing credentials and lock immutable commits.
- Server-safe structured operations execute no commands.
- Batteries-included installation works without manual adapter setup.
