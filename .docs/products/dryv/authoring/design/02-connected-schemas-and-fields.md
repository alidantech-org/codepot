# Connected schemas and field behavior

## Structural authority

Compiled schemas remain structural core objects. Authoring terms such as model, create shape, update shape, query shape, or DTO are conveniences that compile into ordinary schemas and schema-use relationships.

## Reusable properties

Authors can define reusable Python annotations or explicit property refs. A property definition may provide primitive type, format, constraints, documentation, tags, and provenance. Reuse never duplicates semantic identity accidentally.

## Pydantic compilation

The compiler reads supported Pydantic v2 model fields, annotations, defaults, requiredness, unions, collections, enums, nested models, and `Annotated` Codepot metadata. Unsupported validators or arbitrary runtime behavior produce diagnostics rather than leaking Pydantic schemas into IR.

## Connected schema API

A `SchemaAuthor` may provide convenient access to:

- `.ref`;
- typed `.fields` selectors;
- `.pick`, `.omit`, `.partial`, and `.extend`;
- `.derive.create`, `.derive.update`, `.derive.read`, `.derive.query`;
- `.storage(...)` shortcuts that create separate storage mappings;
- `.tags(...)` and `.info(...)`;
- operation/view authoring helpers that still create independent semantic objects.

The connection is authoring ergonomics, not IR ownership collapse.

## Field capabilities

Proposed field capabilities describe stable broad intent:

```text
initialization eligibility
mutation eligibility
visibility/sensitivity
query operators
sortable/selectable capability
semantic reference target
```

They do not automatically create operations, repositories, HTTP parameters, forms, controls, or storage queries.

A capability is activated by an explicit operation or view use. Storage implementation remains mapping-relative.

## Storage-relative field behavior

`stored`, `generated`, `computed`, and virtual/absent behavior belongs to a specific storage mapping. One schema may have several mappings with different behavior.

## Derivation

Derivations must be:

- explicit by name;
- deterministic;
- inspectable;
- provenance-preserving;
- validated against source fields;
- compiled into normal schemas;
- covered by exact relationship tests.

The first version must not silently rewrite public operation boundaries. Debug documents show every derivation step and resulting semantic field ID.

## Relationships

Keep three facts separate:

1. a field semantically references another schema field;
2. a storage mapping connects that reference to a storage relation;
3. a value source provides selectable candidates to an interaction.

This separation supports SQL, document storage, remote services, UIs, CLIs, and tests without making the schema a database entity or HTTP resource.
