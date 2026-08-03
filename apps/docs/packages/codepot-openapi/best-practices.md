---
title: Best practices and troubleshooting
description: Keep typed contracts maintainable, portable, and safe for generators and downstream clients.
product: codepot-openapi
package: codepot-openapi
order: 12
---

# Best practices and troubleshooting

## Organize by domain

Keep one root configuration and split domain declarations into imported modules:

```text
contracts/
├── shared-properties.ts
├── auth/
├── users/
├── orders/
└── frontends/
```

A module may receive the version builder or return a resource builder. Avoid hidden global registries.

## Preserve stable identities

The following names are compatibility boundaries:

- version identifiers;
- component names;
- resource IDs;
- operation IDs;
- entity and relation names;
- access and hook names;
- frontend, screen, and component IDs.

Generated code, cache rules, clients, and template packs may depend on them.

## Prefer semantic metadata

Describe what the application requires, not how one framework implements it.

Good:

```text
operation requires authenticated organiser access
```

Too target-specific:

```text
attach NestJS OrganiserGuard class
```

The framework decision belongs in the template pack.

## Reuse with intent

- Reuse shared properties for truly shared semantics.
- Derive projections when they are views of one canonical model.
- Create separate schemas when business meaning differs.
- Use base entities only for real inherited persistence behavior.

## Keep validation strict

Run both contract and generated-document validation before publishing an API change.

```bash
codepot-openapi validate
```

Use stricter warning behavior in release checks after the team has classified expected warnings.

## Review generated documents

OpenAPI output is a public artifact. Review:

- paths and operation IDs;
- required path parameters;
- request and response content types;
- schema names and refs;
- nullability and optionality;
- security requirements;
- `x-codegen` placement and resolved pointers.

## Avoid raw extension authoring

Use typed builders instead of manually attaching large `x-codegen` objects. Typed builders enforce ownership and reference validation.

## Common failures

### Duplicate schema or operation

Rename or consolidate the declaration. Do not suppress duplicate identity errors.

### Path parameter mismatch

Every `:name` or OpenAPI `{name}` parameter must have a corresponding path parameter declaration with matching spelling.

### Cross-version reference

Refs belong to the version builder that created them. Recreate or share the source definition at the TypeScript helper level instead of passing mutable refs across contracts.

### Cache invalidation target missing

Use exact operation IDs and ensure the target operation is registered in the same contract.

### Frontend operation cannot resolve

Check that the screen or component references the operation's stable ID and belongs to the intended version/frontend registry.

### Generator output is incomplete

First inspect the emitted OpenAPI and `x-codegen`. If the contract is correct, debug the `codepotg` normalized context and template pack rather than adding target-specific fields to the authoring DSL.

## Migration discipline

Treat generated OpenAPI diffs like source-code diffs. A compiler update may expose previously missing metadata or stricter validation. Review output changes before updating downstream generated projects.