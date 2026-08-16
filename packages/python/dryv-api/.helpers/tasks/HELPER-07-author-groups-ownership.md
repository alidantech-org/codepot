# HELPER-07 — Groups, ownership and composition

Status: DONE — PRODUCTION REVIEWED
Prerequisite: HELPER-06 DONE.

## Goal
Make large authored blueprints composable and navigable through explicit grouping/ownership without reintroducing removed compatibility properties.

## Scope
Implement `features/groups/*`, `api/group.py`, ownership composition across all feature registries, and deterministic assembly into the current canonical Group model.

Required capabilities:
- group-scoped declarations with stable fully-owned semantic IDs;
- explicit cross-group references;
- duplicate/ownership collision diagnostics;
- composition of independently authored modules/groups into one Author contract;
- provenance from canonical items back to authored owner/source.

## Enforcement
Do not restore removed `Group.workflows` or other migration properties simply because archived code used them. Canonical Group shape on current `develop` wins. No implicit string-prefix ownership guesses where registry ownership is available.

## Completion
All Author features can be organized/composed through groups and compile into the current canonical Group/Contract shape. Production review confirmed removed group compatibility properties remain absent. No tests were added or run.
