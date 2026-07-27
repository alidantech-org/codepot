# Approved idea: typed Python authoring for the neutral Codepot IR

## 1. Problem

Codepot authoring must not depend on OpenAPI, TypeScript, Node.js, Zod, or any transport format. OpenAPI remains one useful source adapter, but it must not be the foundation of the semantic system.

Developers need a first-class Python package that makes authoring a normal, concise activity:

```text
codepotg-author
```

The package should let a developer define reusable software intent once, connect it through typed references, and compile it into the verbose, rigid, immutable Codepot IR.

## 2. Product thesis

```text
Python authoring ───────────────┐
OpenAPI source adapter ─────────┤
Canonical Codepot IR JSON/YAML ─┼──> one closed Codepot IR
Future native Codepot language ─┘              │
                                               ▼
                                  root-first planning and selection
                                               │
                                               ▼
                                    packs, templates, adapters
```

There is one semantic authority. `codepotg-author` does not create a Contract Graph beside the IR, does not generate files, and does not bypass planning or packs.

## 3. Strong typing model

Python authoring uses several complementary safety layers:

1. Python type annotations, generics, protocols, overloads, `Literal`, `Annotated`, and `Self`.
2. Pyright and mypy for author-time type errors.
3. Pydantic for runtime declaration validation and model-field introspection.
4. Typed Codepot refs for semantic kind safety.
5. A multi-pass ref linker for missing, duplicate, wrong-kind, forward, and cross-author references.
6. Final `codepotg.ir.validate_contract` validation.
7. Strict canonical JSON/YAML decoding and round-trip validation.

Pydantic is an authoring frontend. It is not the final IR and must never leak into templates.

## 4. Typed ref engine

The ref engine is central. Definitions return immutable refs immediately:

```python
User = users.schema(UserModel)
UserCreated = users.event("UserCreated", payload=User)
create_user = users.operation("createUser", ...)
```

Kinds remain distinct:

```text
SchemaRef[T]
FieldRef[T]
OperationRef[TInput, TOutput]
PolicyRef
EventRef[TPayload]
StorageRef[T]
ValueSourceRef[TValue]
ViewRef
PresentationRef
WorkflowRef
WorkflowStepRef
```

Ref identity and ref usage are separate:

```python
User
User.optional()
User.nullable()
User.array()
```

Usage methods return immutable usage values and never mutate the ref target.

Every ref carries an author-session identity. Cross-author refs are rejected unless imported through a future explicit module/export contract.

## 5. Reusable properties and schemas

Authors may use ordinary Python aliases and `Annotated` metadata:

```python
CommonId = Annotated[UUID, cp.field(format="uuid", readonly=True)]
Email = Annotated[EmailStr, cp.field(min_length=3)]
```

Or explicit reusable property refs:

```python
common_id = common.property("id", UUID, format="uuid")
email = common.property("email", EmailStr, min_length=3)
```

Schemas remain structural. Author conveniences such as model, DTO, create shape, or update shape compile into ordinary `Schema` and `SchemaField` values. They do not add parallel IR roots or schema kinds.

Python enums compile to `SchemaKind.ENUM`. Pydantic models compile to structural object schemas.

## 6. Connected schemas without entity drift

A connected schema may expose typed authoring helpers for:

- fields;
- projections;
- derivations;
- field capabilities;
- schema references;
- storage mappings;
- operations that use the schema;
- views and sources that use the schema.

This convenience does not make `entity` a kernel root and does not make a schema an ORM object.

Field capabilities express broad reusable software intent, such as:

- caller initialization eligibility;
- mutation eligibility;
- visibility/sensitivity;
- query operators;
- sorting and selection capability;
- reference to another schema field.

Capabilities do not automatically create endpoints, repositories, query DTOs, forms, or buttons. An operation explicitly exposes a capability; a storage mapping explicitly binds persistence; a view explicitly uses the operation.

Storage state is mapping-relative. A field is stored, generated, computed, or absent in a specific `StorageMapping`; it is not globally a database column.

## 7. Explicit schema derivation

Convenience derivation is allowed:

```python
UserCreate = User.derive.create("UserCreate")
UserUpdate = User.derive.update("UserUpdate")
UserRead = User.derive.read("UserRead")
UserQuery = User.derive.query("UserQuery")
```

Derivation expands to ordinary schemas and records deterministic provenance. Explicit `pick`, `omit`, `partial`, and extension operations remain available. No derived authoring object reaches the IR.

The first implementation must make every derivation inspectable through debug output and exact tests. It must never infer target-language or framework vocabulary.

## 8. Operations and facets

Operations compile into the existing neutral shape:

```text
operation
├── inputs
├── outputs
├── failures
├── effects
└── known facets
```

Authoring sugar such as `query`, `command`, `listener`, or `scheduled` may create ordinary operations with known facts. These words do not become selector roots or new IR object hierarchies.

Known facets remain core-owned. Authoring may provide concise builders for HTTP, access, trigger, execution, and events only when the public IR supports them.

HTTP authoring may connect neutral operation uses to path, query, header, cookie, body, status, response, and cookie/header effects. It must not contain Express, NestJS, FastAPI, controller, middleware, request-object, or response-object implementations.

## 9. Value sources

A field can semantically reference another field while an interactive consumer still needs a way to discover valid values. These are separate facts:

1. semantic field reference;
2. storage relation mapping;
3. candidate value source.

A neutral value source points to an operation and identifies item, value, and label facts. It is not an HTTP route and not frontend fetch code.

The same source can inform web selects, mobile pickers, CLI prompts, generated tests, or documentation.

## 10. Views, parts, and presentations

Views remain group-owned neutral interaction units. Views can contain parts, use schemas, expose sources, and trigger operations.

A presentation is a contract-level neutral application surface that places views from several groups. Examples include an admin application, customer application, driver application, CLI application, documentation portal, desktop application, or conversational surface.

A presentation describes topology and connection:

- identity;
- channel;
- placed views;
- routes/commands/addresses;
- navigation relationships;
- access and guidance.

It does not describe React, Flutter, Next.js, GoRouter, CSS, pixel layout, animation, state libraries, or component libraries.

`Presentation` is a proposed intentional kernel evolution. Until core publishes it, the author package must not hide it in extensions or invent a private IR.

## 11. Guidance and information

Authoring should support concise categorized guidance:

```python
view.info(
    lambda i: i
        .explain("Main admin page for browsing apps.")
        .implement("Render filters above the table and keep pagination in URL state.")
)
```

Guidance is human/AI/template-facing explanation. It never silently creates semantic behavior. Typed facts still require typed declarations.

Guidance is a proposed kernel evolution because it must be preserved, validated, serialized, and exposed consistently.

## 12. Namespaced tags

Tags are first-class immutable Boolean hints available on meaningful semantic objects:

```python
schema.tags("orm:prisma", "orm:prisma:custom_sql")
view.tags("ui:data-table", "ui:filter:advanced")
operation.tags("repository:custom")
```

Safe template access:

```jinja
{% if view.tags.has("ui:filter:advanced") %}
{% endif %}
```

Tags are sorted, unique, serializable, digest-covered, and namespaced. They may guide generation decisions, but they never replace typed refs, relationships, schemas, operations, facets, or known semantic fields.

Tags begin as Boolean hints. They are not a generic key/value programming language. Repeated, stable tag patterns may later be promoted into typed kernel concepts.

Tags are a proposed intentional kernel evolution. They must not be stored only in authoring state if templates and transported IR need them.

## 13. Canonical JSON/YAML

The author compiler must produce:

```text
AuthoringResult
├── contract: Contract | None
├── diagnostics: Diagnostics
├── digest: str
└── optional canonical transport document
```

Required public operations:

```python
result = author.compile()
json_text = result.to_json()
yaml_text = result.to_yaml()
contract = contract_from_json(json_text)
contract = contract_from_yaml(yaml_text)
```

The document is compiled Codepot IR, not a snapshot of Python builders or Pydantic classes.

Transport requirements:

- explicit format and IR versions;
- canonical semantic IDs and `$ref` objects;
- deterministic key and collection ordering;
- strict unknown-field handling;
- no Python class names or memory addresses;
- no authoring refs, builders, callables, registries, or parser objects;
- JSON/YAML semantic parity;
- `decode(encode(contract)) == contract`;
- validation after decoding;
- canonical JSON as digest/signature input;
- pretty JSON/YAML for debugging and shipping.

A transported IR document can be loaded directly as a semantic input. Unlike OpenAPI, it requires strict decoding rather than semantic inference.

## 14. Compiler pipeline

```text
collect declarations
→ freeze author session
→ validate authoring models
→ assign deterministic IDs
→ build typed ref index
→ resolve forward/cross references
→ expand reusable properties
→ compile structural schemas/enums
→ expand projections and derivations
→ compile field capabilities supported by core
→ compile storage mappings
→ compile policies/events
→ compile operations, effects, and known facets
→ compile value sources/views/presentations when core supports them
→ compile workflows
→ construct immutable core Contract
→ run core validation
→ canonicalize and digest
→ optionally serialize JSON/YAML
```

Expected user errors return structured diagnostics with declaration source, expected kind, actual kind, referencing declaration, and stable codes. Normal invalid declarations must not escape as raw Pydantic or Python exceptions.

## 15. Boundaries

`codepotg-author` does not:

- create a second semantic graph;
- add private semantic nodes or facets;
- use arbitrary `meta` dictionaries as semantic behavior;
- register selectors or template variables;
- model runtime algorithms;
- model database/framework-specific APIs;
- render source code;
- choose packs/templates/paths;
- write files or execute commands;
- make manual OpenAPI writing the authoring model;
- depend on CodepotG 1.0.0 internals;
- use process-global registries.

The locked principle is:

> Python may be expressive at author time while compiled Codepot IR remains closed, deterministic, neutral, portable, readable, and selector-safe.
