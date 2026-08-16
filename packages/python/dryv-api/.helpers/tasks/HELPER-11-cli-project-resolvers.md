# HELPER-11 — CLI project model and resolvers

Status: DONE
Prerequisite: HELPER-10 DONE.

## Goal
Rebuild dryv-cli as a modular reference Project Client starting with local project discovery and resource resolution.

## Implemented owners
`project/` owns deterministic project discovery, locator-only configuration and project snapshots.
`resolvers/` owns direct IR/Author source location, local pack/resource bundling and destination boundaries.

## Enforced boundary
CLI resolves **where/how to obtain inputs** only. Runtime remains authoritative for dryv.yaml meaning, pack manifests, selectors, contexts, dependencies and output planning. Resolvers perform no generated-file writes and the old monolithic Project Client is not used by this path.

## Completion
The CLI can discover and collect the explicit uploads required by dryv-api without importing Runtime internals. No tests were added or run.
