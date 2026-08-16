# HELPER-03 — Properties, schemas, projections and types

Status: DONE — PRODUCTION REVIEWED
Prerequisite: HELPER-02 DONE.

## Goal
Provide a strong reusable schema authoring experience and compile it cleanly into current canonical Property/Schema/type concepts.

## Scope
Implement `features/properties/*`, `features/schemas/*`, and the cross-feature type/projection resolution they require.

Required capabilities:
- reusable named properties with constraints/metadata;
- inline and referenced fields without losing provenance;
- canonical primitive/composite/reference type conversion;
- schema fields, inheritance/extension where Canonical IR supports it;
- projection authoring such as pick, omit and partial;
- projection chains resolved deterministically before canonical emission;
- typed schema/property refs and dependency ordering;
- errors for unknown/duplicate/incompatible fields and invalid projections.

## Enforcement
Projection instructions are Author conveniences, not new Runtime IR semantics. Do not reintroduce OpenAPI/Zod-specific meaning into generic Dryv Author. Do not flatten reusable Property semantics into arbitrary field dictionaries when Canonical IR has an explicit concept.

## Completion
Users can author reusable properties and rich schemas concisely; compiler produces explicit current Canonical IR items with deterministic IDs and references. Production review confirmed the canonical mapping. No tests were added or run.
