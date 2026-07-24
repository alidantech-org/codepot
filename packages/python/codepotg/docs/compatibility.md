# Compatibility Policy

The normalized-contract expansion preserves the established CodepotG package design and public behavior.

## Non-breaking rules

1. Existing global template variables remain available.
2. Existing properties are not renamed or removed during normalization.
3. New normalized structures are additive.
4. Existing dictionary metadata remains available while named replacements are introduced.
5. Bundled template packs continue to generate throughout the migration.
6. Project-owned template packs receive safe defaults for newly added optional values.
7. OpenAPI 3.0 and 3.1 remain supported.
8. Existing task configuration, path selection, import planning, write policy, CLI behavior, and emission boundaries remain unchanged unless a separate compatible feature explicitly extends them.
9. Language-neutral contracts never contain target-language syntax.
10. No source information is silently discarded.

## Migration sequence

```text
add normalized value
  -> add compatibility alias
  -> migrate bundled packs
  -> document replacement
  -> emit deprecation diagnostic
  -> retain compatibility for an approved support window
```

Removal is outside the normalized-contract implementation unless separately reviewed and approved.

## Existing output baseline

Before implementation, CodepotG records:

```text
existing test results
existing lint results
representative generated output
current debug output
current template variable inventory
current bundled language-pack behavior
```

Every implementation batch compares against this baseline.

## Contract versioning

The template contract keeps an explicit version. Additive fields do not require templates to change. Any incompatible proposal requires a new contract version and an explicit compatibility bridge.

## Safe defaults

Missing optional values use predictable empty values:

```text
empty tuple for ordered collections
empty lookup for maps
false for disabled feature flags
explicit unset value where null is meaningful
none only where absence is already part of the stable contract
```

Templates should not fail because a document omits optional metadata.

## Alias behavior

A compatibility alias must point to the same normalized fact rather than duplicate inference. Aliases are tested for equivalent values.

Examples include top-level collection aliases and legacy metadata paths retained while named structures are adopted.

## OpenAPI compatibility

CodepotG normalizes source-version differences while preserving source representation:

```text
OpenAPI 3.0 nullable behavior
OpenAPI 3.1 type unions
exclusive-bound differences
JSON Schema dialect information
supported and unsupported JSON Schema keywords
```

A source-version-specific value remains available through raw preservation even when no normalized helper exists yet.

## Language-adapter compatibility

Adding an adapter cannot alter facts consumed by existing adapters. When a new target exposes a missing language-neutral need, the API contract is extended additively and all existing adapters remain valid.

Adapters use the shared protocol, naming provider, dependency planning, path planning, and emission engine.

## Template-pack compatibility tests

Compatibility coverage includes:

```text
global variable existence
contextual variable existence
legacy alias equivalence
safe empty metadata
name variant stability
collection ordering
lookup correctness
reference preservation
existing generated-output snapshots
custom template-pack smoke tests
```

## Data-loss gate

Normalization diagnostics classify values as:

```text
typed
resolved
preserved extension
preserved raw-only
unsupported but preserved
malformed but preserved
lost
```

A release cannot pass the completeness gate while any value is classified as lost.

## Commit policy

Implementation is divided into small reversible commits. Each commit must:

```text
keep tests green or document a pre-existing failure
preserve existing public paths
include focused tests for new facts
update affected documentation
avoid unrelated refactors
```

## Release policy

The package remains publishable throughout the migration. A batch that breaks existing bundled packs, clean-wheel validation, CLI startup, OpenAPI compatibility, or guarded emission is not complete.
