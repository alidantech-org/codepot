# Writers, cache, commands, and security tasks

## WRITE-001 — Artifact writer port

**Status:** planned

**Dependencies:** PLAN-008, CORE result/event contracts

- [ ] Define writer request/result, staged artifact, diff status, lifecycle, ownership, and rollback outcome.
- [ ] Keep writer independent from templates and source adapters.
- [ ] Support text and binary content.

## WRITE-002 — Memory writer

**Status:** planned

**Dependencies:** WRITE-001

- [ ] Store immutable planned artifacts in memory.
- [ ] Preserve deterministic order and metadata.
- [ ] Enforce the same collision/path/lifecycle validation as filesystem output.
- [ ] Add server/playground tests.

## WRITE-003 — Archive writer

**Status:** planned

**Dependencies:** WRITE-001

- [ ] Produce deterministic ZIP or selected archive format.
- [ ] Normalize metadata that would make archives non-reproducible.
- [ ] Preserve executable mode only through explicit artifact metadata.
- [ ] Reject traversal and duplicate entries.

## WRITE-004 — Transactional filesystem writer

**Status:** planned

**Dependencies:** WRITE-001

- [ ] Stage all creates/changes/deletes in a private output-root-contained or secure temporary area.
- [ ] Validate destination roots, symlink containment, case collisions, reserved names, and permissions.
- [ ] Compare exact bytes or documented line-ending policy.
- [ ] Prepare backup/replace operations.
- [ ] Commit in a deterministic sequence.
- [ ] Roll back on partial failure and report platform limitations honestly.
- [ ] Ensure cancellation before commit leaves destination unchanged.

**Prohibited shortcut:** per-file `os.replace` presented as a whole-generation transaction without rollback coordination.

## WRITE-005 — Lifecycle and ownership manifest

**Status:** planned

**Dependencies:** WRITE-004

- [ ] Implement managed, immutable, protected, and unmanaged behavior.
- [ ] Record pack/instance/artifact/source/digest/lifecycle ownership.
- [ ] Protect user-created or differently owned files.
- [ ] Restrict cleanup to project-approved scopes and owned files.
- [ ] Add adoption/recovery diagnostics for missing or corrupted manifests.

## WRITE-006 — Dry run and diff inspection

**Status:** planned

**Dependencies:** WRITE-002, WRITE-004

- [ ] Report create/change/delete/leave and exact ownership implications.
- [ ] Support optional memory rendering without commit.
- [ ] Include unresolved actions and commands.
- [ ] Ensure dry run never mutates destination or approval stores.

## CACHE-001 — Content-addressed cache contract

**Status:** planned

**Dependencies:** version primitives, source/pack/plugin digests

- [ ] Define cache keys containing all behavior-affecting inputs.
- [ ] Define immutable read/write result and corruption diagnostics.
- [ ] Separate compiled-template, normalized-source, selection/plan, and rendered-artifact namespaces where useful.
- [ ] Add configurable size/entry limits and eviction metadata.

## CACHE-002 — Filesystem cache implementation

**Status:** planned

**Dependencies:** CACHE-001

- [ ] Write through temp/fsync/replace safely.
- [ ] Validate digests on read.
- [ ] Quarantine or remove corrupted entries.
- [ ] Prevent path traversal and cross-user unsafe permissions.
- [ ] Avoid loading large entries fully when streaming is supported.

## CMD-001 — Security policy model

**Status:** planned

**Dependencies:** CFG security model

- [ ] Implement host, user, project, pack, and approval layers.
- [ ] Implement strictest-wins resolution.
- [ ] Define local trusted, untrusted clone, and server-safe presets.
- [ ] Define command capabilities and risk levels.
- [ ] Prove configuration cannot weaken host policy.

## CMD-002 — Command and action plan

**Status:** planned

**Dependencies:** CMD-001, PLAN-009

- [ ] Implement structured raw command and typed action descriptors.
- [ ] Record owner, phase, executable/action payload, cwd, timeout, optional state, permissions, environment allowlist, and source span.
- [ ] Produce stable command digests.
- [ ] Separate desired manifest state from installation/action execution.

## CMD-003 — Approval store

**Status:** planned

**Dependencies:** CMD-002, lock identity

- [ ] Implement approval scope `once` and exact digest.
- [ ] Include pack source/commit/subdirectory/manifest digest and exact command/capabilities.
- [ ] Invalidate on any relevant change.
- [ ] Never serialize secrets.
- [ ] Provide inspect/revoke operations.

## CMD-004 — Safe executor

**Status:** planned

**Dependencies:** CMD-001..CMD-003

- [ ] Execute without shell by default.
- [ ] Apply cwd containment, filesystem permissions, environment allowlist, and network policy where enforceable.
- [ ] Implement timeout, cancellation, stdout/stderr bounds, and process-tree cleanup.
- [ ] Distinguish required/optional failure.
- [ ] Redact secrets and credentials from events/diagnostics.

## CMD-005 — Transaction phase integration

**Status:** planned

**Dependencies:** CMD-004, WRITE-004

- [ ] Run staged-output actions before commit when declared.
- [ ] Run project-state validation after commit when declared.
- [ ] Report which actions participate in transactional rollback and which do not.
- [ ] Handle on-failure actions without masking the primary error.

## Acceptance gate

- Memory and filesystem output share the same artifact semantics.
- Exact comparison never ignores comments/whitespace/layout.
- User files and protected paths are safe.
- Cache keys change for every behavior input.
- Server-safe policy executes nothing.
- Pack approval is invalidated by changed Git commit, manifest, command, or capability.
- Timeouts and cancellation clean up child processes.
