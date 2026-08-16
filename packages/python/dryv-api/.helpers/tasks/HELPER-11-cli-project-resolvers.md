# HELPER-11 — CLI project model and resolvers

Status: DONE — PRODUCTION REVIEWED
Prerequisite: HELPER-10 DONE.

## Goal
Rebuild dryv-cli as a modular reference Project Client starting with local project discovery and resource resolution.

## Implemented owners
`project/` owns deterministic project discovery, strict locator-only configuration and project snapshots.
`resolvers/` owns direct IR/Author source location, local/Git pack bundling, explicit project resources and destination boundaries.

Git packs use the user's normal Git installation/configuration/credentials, require an explicit ref, support an optional pack subdirectory, exclude repository metadata and reject symlink/root escapes before exact bytes are uploaded.

## Enforced boundary
CLI resolves **where/how to obtain inputs** only. Runtime remains authoritative for dryv.yaml meaning, pack manifests, selectors, contexts, dependencies and output planning. Resolvers perform no generated-file writes and the old monolithic Project Client is not used by this path.

`source.resource` remains reserved for a future explicit pre-resolved pack-bundle resource contract; the CLI fails clearly rather than inventing hidden bundle conventions.

## Completion
The CLI can discover and collect the explicit uploads required by dryv-api for direct IR/Author input and local or Git-backed packs without importing Runtime internals. Production review also hardened duplicate-key/source validation and Jinja template media types. No tests were added or run.
