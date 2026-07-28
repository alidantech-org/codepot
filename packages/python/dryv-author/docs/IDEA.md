# Approved idea: typed Python authoring for Dryv

## Problem

Developers need a concise, strongly typed way to define reusable software meaning without coupling authoring to a target language, framework, database, transport file, template, or output layout.

`dryv-author` provides that authoring experience and compiles it into the closed immutable `dryv.ir.Contract` understood by the Dryv runtime.

## Product thesis

```text
typed Python authoring -----------+
canonical Dryv IR transport ------+--> one closed Dryv Contract
future native Codepot language ---+             |
                                                v
                                   planning, packs, templates,
                                   plugins, and managed output
```

There is one semantic authority. The authoring package does not create a second graph, generate files, select packs, or bypass runtime planning.

## Safety layers

Python authoring combines:

1. Python type annotations, generics, protocols, overloads, `Literal`, `Annotated`, and `Self`.
2. Pyright and mypy for author-time feedback.
3. Pydantic for runtime declaration validation and model introspection.
4. Typed Dryv references for semantic kind safety.
5. A deterministic multi-pass linker for missing, duplicate, wrong-kind, forward, and foreign-session references.
6. Final `dryv.ir.validate_contract` validation.
7. Optional strict canonical JSON/YAML round trips owned by the Dryv runtime.

Pydantic is an authoring frontend. Pydantic classes and builder objects never enter the compiled contract or template context.

## Typed reference engine

Definitions return immutable typed references immediately:

```python
User = accounts.schema(UserModel)
UserCreated = accounts.event("UserCreated", payload=User)
create_user = accounts.operation("createUser", output=User)
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

Reference identity and usage are separate:

```python
User
User.optional()
User.nullable()
User.array()
```

Usage methods return immutable values. Every reference belongs to one author session; foreign-session references fail unless a future explicit import/export contract resolves them.

## Reusable properties and structural schemas

Authors may use ordinary Python aliases and `Annotated` metadata:

```python
CommonId = Annotated[UUID, cp.field(format="uuid", readonly=True)]
Email = Annotated[EmailStr, cp.field(min_length=3)]
```

Or explicit reusable property references:

```python
common_id = common.property("id", UUID, format="uuid")
email = common.property("email", EmailStr, min_length=3)
```

Schemas remain structural. Author conveniences such as create, update, read, and query shapes compile into ordinary `Schema` and `SchemaField` values rather than parallel kernel roots.

Python enums compile to enum schemas. Pydantic models compile to structural object schemas.

## Connected schemas without entity drift

A schema authoring handle may expose typed helpers for:

- fields;
- projections and derivations;
- field capabilities;
- schema references;
- storage mappings;
- operations that use the schema;
- views and value sources that use the schema.

This convenience does not turn a schema into an ORM entity.

Field capabilities express reusable intent such as initialization, mutation, visibility, sensitivity, querying, sorting, selection, and references. Capabilities never automatically create endpoints, repositories, forms, or controls. Operations expose behavior explicitly; storage mappings bind persistence explicitly; views use operations explicitly.

Storage state is mapping-relative. A field may be stored, generated, computed, or absent in one mapping without becoming a global database column.

## Explicit derivation

Convenience derivation is allowed:

```python
UserCreate = User.derive.create("UserCreate")
UserUpdate = User.derive.update("UserUpdate")
UserRead = User.derive.read("UserRead")
UserQuery = User.derive.query("UserQuery")
```

Derivation expands into ordinary schemas with deterministic provenance. Explicit `pick`, `omit`, `partial`, and extension operations remain available. Derivation never introduces target-language or framework vocabulary.

## Operations and known facets

Operations compile into the neutral shape:

```text
operation
├── inputs
├── outputs
├── failures
├── effects
└── known facets
```

Authoring sugar such as `query`, `command`, `listener`, or `scheduled` may create ordinary operations with known facts. These words do not become selector roots or new semantic hierarchies.

Known facets remain core-owned. Authoring may provide concise builders only when the public IR publishes the corresponding typed facts.

## Value sources

A field reference, storage relationship, and candidate-value source are separate facts.

A value source points to an operation and identifies item, value, and label facts. It is not a route or frontend fetch implementation. The same source may inform web controls, mobile pickers, CLI prompts, generated tests, or documentation.

## Views and presentations

Views are group-owned neutral interaction units. They may contain parts, use schemas, expose value sources, and trigger operations.

A presentation is a neutral application surface that places views from several groups. It may represent an admin application, customer application, mobile application, CLI application, documentation portal, desktop application, or conversational surface.

A presentation describes identity, channel, placed views, routes or addresses, navigation relationships, access, and guidance. It does not describe component libraries, CSS, pixel layout, animations, framework routers, or state-management libraries.

## Guidance

Authoring should support categorized guidance:

```python
view.info(
    lambda i: i.explain("Main admin page for browsing apps.").implement(
        "Keep filters above the table and pagination in URL state."
    )
)
```

Guidance explains intent to humans, AI tools, and templates. It never silently creates semantic behavior.

## Namespaced tags

Tags are immutable Boolean hints on meaningful semantic objects:

```python
schema.tags("orm:custom")
view.tags("ui:data-table", "ui:filter:advanced")
operation.tags("repository:custom")
```

Tags are sorted, unique, serializable, digest-covered, and namespaced. They may guide pack behavior but never replace typed references, relationships, schemas, operations, facets, or known fields.

## Canonical transport

The author compiler returns the in-memory contract and diagnostics:

```text
AuthoringResult
├── contract: Contract | None
└── diagnostics: Diagnostics
```

Optional JSON/YAML transport belongs to the Dryv runtime:

```python
result = author.compile()
contract = result.require_contract()
json_text = dryv.ir.contract_to_json(contract)
yaml_text = dryv.ir.contract_to_yaml(contract)
```

Transport contains compiled Dryv IR, never Python builders, Pydantic classes, callables, registries, or parser objects.

## Compiler pipeline

```text
collect declarations
→ freeze author session
→ validate authoring models
→ assign deterministic IDs
→ build typed reference index
→ resolve references
→ expand reusable properties
→ compile structural schemas and enums
→ expand projections and derivations
→ compile supported field capabilities
→ compile storage mappings
→ compile policies and events
→ compile operations, effects, and known facets
→ compile value sources, views, and presentations
→ compile workflows
→ construct immutable Contract
→ validate with Dryv core
```

Invalid declarations return structured diagnostics with stable codes and source context. Ordinary user errors must not escape as raw Pydantic or Python exceptions.

## Boundaries

`dryv-author` does not:

- create a second semantic graph;
- add private semantic nodes or facets;
- use arbitrary metadata dictionaries as semantic behavior;
- register selectors or template variables;
- model runtime algorithms;
- model framework- or database-specific APIs;
- render source code;
- choose packs, templates, or paths;
- write generated files or execute commands;
- own transport serialization;
- depend on archived runtime internals;
- use process-global registries.

The locked principle is:

> Python may be expressive at author time while compiled Dryv IR remains closed, deterministic, neutral, portable, readable, and selector-safe.
