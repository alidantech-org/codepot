# HELPER-06 — Workflows, views and presentations

Status: DONE — PRODUCTION REVIEWED
Prerequisite: HELPER-05 DONE.

## Goal
Implement the higher-order behavior/presentation concepts that make Dryv Author capable of describing more than simple CRUD contracts.

## Scope
Implement `features/workflows/*`, `features/views/*`, and `features/presentations/*`.

Workflow authoring must cover the current IR's meaningful structures through dedicated owners for steps, transitions, decisions/cases, refs and resolution. It must support explicit operation/event relationships and state/control flow without burying all behavior in one WorkflowDeclaration.

Views must own view declarations/builders/triggers/references and compile to current canonical View concepts. Presentations must remain neutral software/presentation meaning, not framework-specific UI code generation.

## Enforcement
No hidden workflow execution engine in Author. Author describes and validates meaning; it does not run workflows. No frontend framework conventions or template paths.

## Completion
Workflows, views and presentations compile deterministically through current Canonical IR. Production review additionally hardened presentation navigation parent existence/cycle validation. No tests were added or run.
