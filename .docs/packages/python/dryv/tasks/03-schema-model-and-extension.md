# Task 03 — Complete Schema semantics and single-base extension

Status: [x]
Owner: `packages/python/dryv`
Depends on: Task 02
Validation: schema-model tests, inheritance resolution tests, transport round trips

> Implementation is complete on `develop`. External executable certification is still pending because the connected environment exposes no repository checkout or CI runner. See [`../PROGRESS-00-10.md`](../PROGRESS-00-10.md).

## Goal

Harden `Schema` as the one canonical structural concept and implement the approved single-base extension model without turning Schema into an ORM entity or generated DTO model.

## Canonical Schema responsibilities

Schema owns structural meaning including:

- identity and name;
- schema kind/type expression;
- fields;
- requiredness/nullability/read-only facts where structurally meaningful;
- intrinsic constraints and formats;
- field capabilities as a separate typed concern;
- references to other Schemas/Properties;
- documentation, tags, guidance and provenance;
- zero or one direct base Schema reference.

Schema may be used anywhere typed structure is required: operation I/O, event payloads, workflow I/O, view data, nested fields and other semantic relationships. Do not create context-specific schema root kinds.

## Approved extension rules

A Schema may extend zero or one direct base Schema.

```text
BaseResponse
    ↑
PagedResponse extends BaseResponse
    ↑
UserListResponse extends PagedResponse
```

Requirements:

- transitive extension chains are supported;
- multiple direct bases are invalid;
- extension cycles are invalid;
- extending a Schema never mutates the base;
- a derived Schema has its own semantic identity;
- a derived Schema may add fields, including fields typed by another Schema;
- inherited field provenance must remain inspectable;
- overrides must be explicit;
- incompatible overrides must fail validation;
- effective Schema resolution must be deterministic.

Example meaning:

```text
UserResponse extends BaseResponse
adds:
    user: UserSchema
```

## Extension versus composition

Do not use `extends` for every kind of reuse. Normal nested Schema references remain composition. Schema mapping/projection behavior remains separate and must not be silently collapsed into inheritance.

## Field capabilities

Preserve the approved separation:

```text
Field structural facts
!=
Field capabilities
```

Capabilities may express approved semantic uses such as initialization/create eligibility, mutation/update eligibility, visibility/sensitivity, query/filter behavior, sortable/selectable behavior and similar neutral facts. Do not encode framework form controls or ORM decorators.

## Relationships outside Schema

Schema may be a connected authoring hub, but canonical reverse relationships such as operations using a Schema or storage mappings for it are derived/indexed by Runtime rather than duplicated as authored Schema-owned lists.

Schema extension does not automatically inherit Operations or StorageMappings.

## Non-goals

- Do not add ORM/entity inheritance behavior.
- Do not add generated-code class/interface semantics.
- Do not finalize broad schema-projection syntax that remains under review.
- Do not create event/workflow/request/response-specific Schema root types.

## Allowed paths

- `packages/python/dryv/src/dryv/ir/schemas/**`
- IR type/reference/kernel files required by Schema
- corresponding tests and canonical Dryv docs

## Acceptance criteria

- Schema has zero/one direct base reference.
- Full extension chains resolve correctly and preserve origin information.
- Multiple inheritance/cycles/silent incompatible overrides are rejected.
- Nested Schema references work independently of extension.
- Field capabilities remain typed and separate from structural field facts.
- Serialization can represent direct-base information portably and deterministically.

## Validation

Add tests for no-base, one-level, multi-level, nested-schema fields, explicit override, invalid override, cycle, multiple-base rejection and deterministic effective-field ordering. Run all Dryv IR/architecture tests and `git diff --check`.
