# Dryv author foundation audit

**Audit date:** 2026-07-27  
**Branch:** `chatgpt/codepotx-restart-dryv-author`  
**Merged foundation:** `43aa0a1894a6128a086bea203883a907f3c8c885`

## Scope

Reviewed the merged author session, refs, options, diagnostics, declarations, structural schema API, and focused unit tests against the approved package boundary and current public `dryv` facades.

## Findings corrected in this batch

### AUTHOR-AUDIT-001 — duplicated diagnostics model

The package defined a second diagnostic/severity/collection model instead of consuming `dryv.diagnostics`. This created incompatible result types and violated the public-facade-only boundary.

**Correction:** `AuthorDiagnostic`, `AuthorDiagnostics`, and `AuthorDiagnosticSeverity` now alias the public core types.

### AUTHOR-AUDIT-002 — unsupported kinds could enter declarations

`RefKind.VALUE_SOURCE` and `RefKind.PRESENTATION` were registered in the generic declaration map even though the current core IR has no approved representation.

**Correction:** generic declaration rejects both before mutation, records exact `AUTHOR_CORE_UNSUPPORTED`, and leaves the declaration set unchanged.

### AUTHOR-AUDIT-003 — module-global mutable session counter

Session IDs were allocated through a module-global counter and lock. It was not a registry, but it introduced unnecessary global mutable process state.

**Correction:** each `Author` now owns a random opaque session identity created without a mutable package-global counter.

## Remaining audit findings

1. `Author.property(..., **options)` still relies on an unchecked dynamic keyword bridge and a type-ignore. Replace it with a typed `FieldOptions` parameter or overloads.
2. Schema declarations are authoring-only and are not yet compiled into public `dryv.ir` values.
3. Operation, event, policy, storage, view, and workflow methods currently allocate refs without typed payload builders. They must not be considered implemented until compiler mappings and tests exist.
4. Enum values are currently normalized to strings; compilation must validate this against the public enum-value contract.
5. No complete package lint, static typing, build, wheel install, or real-core integration evidence has been reproduced yet.
6. Pydantic v2 recursion, projection expansion, deterministic compiler passes, and canonical JSON/YAML transport remain outstanding.

## Boundary verdict

The corrected foundation is safe to continue building on, but it is not feature-complete or release-ready. The task claim remains `in_progress`.
