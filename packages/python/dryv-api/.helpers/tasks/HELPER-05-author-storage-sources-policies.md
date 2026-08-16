# HELPER-05 — Storage, value sources and policies

Status: DONE — PRODUCTION REVIEWED
Prerequisite: HELPER-04 DONE.

## Goal
Implement three distinct semantic feature families without hiding them as schema flags or UI metadata.

## Scope
Implement `features/storage/*`, `features/sources/*`, and `features/policies/*`.

Required storage capabilities include explicit schema/storage mappings, storage fields/mapping relationships and typed refs. `database=True` on a schema must not replace canonical StorageMapping meaning.

Required ValueSource capabilities include operation, output, value field, label fields, optional search input and explicit dependency inputs/sources, matching the current IR's first-class ValueSource concept.

Required policy capabilities include named policy declarations, references and canonical relationships supported by current IR.

## Enforcement
Keep all relationships explicit and deterministic. A convenience builder may reduce repetition but may not hide semantic items that must exist in Canonical IR.

## Completion
Storage, ValueSource and Policy declarations compile independently and compose through explicit references into current Canonical IR. Production review confirmed their constructor mappings and separation. No tests were added or run.
