# Phase 13 — Strict TypeScript recovery

Status: IN PROGRESS
Issue: #9

## Goal

Restore clean TypeScript 7 typechecking after the first installed Windows workspace validation exposed corrupted source, exact-optional construction defects, index-signature access defects, stale event names, and workspace subpath resolution issues.

## Completed fixes

- [x] replace the corrupted non-UTF-8 authoring compiler
- [x] remove the deleted TypeScript 7 `baseUrl` option
- [x] resolve CLI workspace package subpaths through `paths`
- [x] add isolated-declaration parameter and callback annotations
- [x] normalize docs line endings and make advisory docs validation warning-only
- [x] construct exact optional artifact fields only when defined
- [x] use strict bracket access for dynamic JSON and module export records
- [x] remove ambiguous authoring type re-exports
- [x] publish generation events through stable event names and payloads
- [x] keep template context operation effects JSON-safe
- [x] adapt to the current non-generic `tsx` `tsImport` signature

## Validation required

- [ ] `pnpm --filter codepotx typecheck`
- [ ] `pnpm --filter codepotx-cli typecheck`
- [ ] `pnpm --filter @codepot/site typecheck`
- [ ] `pnpm typecheck`
- [ ] `pnpm --filter codepotx build`
- [ ] `pnpm --filter codepotx-cli build`
- [ ] `pnpm --filter @codepot/site build`

## Completion rule

Keep issue #9 open until the installed Windows checkout reports clean package typechecks and builds. Record every remaining compiler batch here before closing the phase.
