# Skill: propose architecture change

## Use when

A requirement appears to need a new semantic concept, package boundary, plugin capability, selector, configuration contract, ownership rule, or generation behavior.

## Procedure

1. Prove the problem with real use cases.
2. Show why current concepts cannot represent it safely.
3. Identify alternatives, including no change.
4. Define affected architecture, IR, contexts, selectors, configuration, packages, and public APIs.
5. Analyze compatibility, migration, determinism, security, caching, locking, and traceability consequences.
6. Record the proposal under the owning package or app documentation folder.
7. Define required documents, tests, versions, and later implementation tasks.
8. Request explicit approval.
9. Do not implement or create an implementation task before approval.

## Output

An item-local proposal under `.docs/packages/<ecosystem>/<package>/` or `.docs/apps/<app>/`.
