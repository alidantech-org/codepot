# HELPER-08 — Compiler context and deterministic pipeline

Status: TODO
Prerequisite: HELPER-07 DONE.

## Goal
Assemble the feature modules into a real deterministic Author compiler rather than a giant conditional conversion function.

## Scope
Implement `compiler/compiler.py`, `pipeline.py`, `compiler/context/*`, global `compiler/resolvers/*`, and `compiler/passes/*`.

Required `CompilerContext` state: author metadata, declarations, symbols, name/semantic-ID registry, ownership registry, resolved refs, normalized declarations, compiled canonical items and diagnostics.

Required explicit phases:
`REGISTER → VALIDATE DECLARATIONS → RESOLVE REFERENCES → RESOLVE DERIVED AUTHORING → COMPILE FEATURES → ASSEMBLE GROUPS → CREATE CONTRACT → CANONICAL IR VALIDATION`.

Feature compiler ordering must be a visible static contract, not entry-point/plugin discovery. Feature-specific resolving stays inside feature modules; compiler-wide resolvers handle only genuinely cross-feature concerns such as generic refs/types/projections/dependencies.

## Enforcement
No mutable module globals, hidden passes, renderer/pack/filesystem behavior, or compatibility path. Keep orchestration files small; split domain logic back to feature owners rather than growing compiler.py.

## Completion
One public compiler path produces the current Canonical `Contract` plus diagnostics deterministically and invokes Dryv canonical validation after author compilation. No tests yet.