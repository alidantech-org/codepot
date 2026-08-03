# Skill: propose architecture change

## Use when

A requirement appears to need a new semantic concept, package boundary, plugin capability, selector, configuration contract, ownership rule, or generation behavior.

## Procedure

1. Prove the problem with real use cases.
2. Show why current concepts cannot represent it safely.
3. Identify alternatives, including no change.
4. Define affected architecture, IR, contexts, selectors, configuration, packages, and public APIs.
5. Analyze compatibility, migration, determinism, security, caching, locking, and traceability consequences.
6. Define required documents, tests, versions, and tasks.
7. Request explicit approval.
8. Do not implement before approval and document updates.

## Output

A proposal based on `.docs/tasks/templates/architecture-proposal.md`.
