## Yes—Python can provide enough safety, but Pydantic alone is not the answer

The right stack is:

```text
Python static typing
    + strict Pyright/mypy
    + Pydantic runtime validation
    + typed Codepot refs
    + a multi-pass ref compiler
    + final core IR validation
```

This can make authoring feel almost as safe and convenient as the current TypeScript `codepot-openapi`.

Python supports generics, protocols, `Literal`, `Annotated`, `Self`, overloads, and `dataclass_transform`; these are enough to build typed fluent APIs and teach type checkers about custom model builders. ([Typing Documentation][1])

Pydantic adds runtime model validation, typed model construction, frozen-model enforcement, `Annotated` metadata, and additional mypy integration. It does not replace a static checker, and it does not automatically create Codepot’s ref system. ([Pydantic Docs][2])

So the package should not merely be “Pydantic models for the IR.” It should be:

> **A typed Python authoring compiler whose declarations and Pydantic models compile into the rigid Codepot IR.**

---

# What makes the existing Node authoring successful

I reviewed the current `packages/nodejs/codepot-openapi` authoring and compiler implementation, plus the older archived authoring and IR attempt.

The current package succeeds because it combines four important mechanisms.

## 1. Definitions immediately return typed refs

The normal user experience is:

```ts
const shared = v1.defineProperties('Shared', {
  id: z.string().uuid(),
  email: z.string().email(),
}).ref;

const schemas = users.defineSchemas({
  User: {
    id: shared.id,
    email: shared.email,
  },
}).ref;
```

A definition is registered once and immediately becomes reusable. The user never manually writes a `$ref`, component path, or duplicate schema.

## 2. Refs are more than strings

A ref carries:

* a stable internal ID;
* a kind;
* a name;
* its target metadata;
* type-level information;
* usage methods.

The usage layer supports:

```text
optional
required
nullable
nonNullable
array
extendWith
pick
omit
partial
```

The TypeScript mapped types constrain projection keys to fields that actually exist on the source schema.

The implementation keeps those methods non-enumerable so authoring behavior does not leak into serialized definitions.

## 3. Resolution happens after collection

The compiler does not require every final output name to be known while authoring.

It first builds resolver maps across:

* shared properties;
* schemas;
* parameters;
* request bodies;
* responses;
* resources;
* frontends.

Only after the registries are populated does it compile definitions and replace pending references.

The main compile pipeline:

1. collects access and DTO-role usage;
2. compiles components;
3. compiles paths;
4. compiles inferred components;
5. creates metadata;
6. resolves pending refs;
7. returns the final document.

Validation happens before a compile result is considered successful.

## 4. Authoring is concise because the compiler expands it

The user writes:

```ts
route.post('/').body(CreateUser).response(User)
```

The compiler creates the verbose OpenAPI operation, schemas, refs, response structures, resource metadata, DTO roles, access data, and `x-codegen`.

That same principle should drive `codepotg-author`:

> Users author concise intent. The author compiler expands it into complete, rigid IR.

---

# What the archived rewrite teaches us

The archive confirms that this is not a new idea for Codepot. It already attempted a separate authoring layer and compiled IR.

The archived architecture explicitly distinguished:

```text
VersionAuthoringState
        ↓
multi-pass compiler
        ↓
CodepotDefinition
```

The `VersionBuilder` documented that its state was authoring state, not final IR, and exposed a snapshot for debugging.

It also had typed authoring refs with:

* `id`;

* `kind`;

* `key`;

* a phantom type target;

* usage wrappers;

* optional, nullable, array, and extension behavior.

The compiler was correctly organized into ordered passes:

```text
content types
properties
entities
relations
field sets
models
schemas
security
errors
resources
metadata
ref validation
```

And the compiled format used portable JSON/YAML `$ref` values rather than leaking authoring objects.

Those are all ideas worth retaining.

## Why that attempt still became unsuitable

Its semantic center became too specific:

```text
properties
entities
field_sets
models
dtos
params
resources
routes
errors
security
```

For example, the old schema registry was permanently divided into entity, field-set, model, DTO, and params registries.

The authoring ref kinds repeated those same categories and included resource and route identities as primary concepts.

It also accumulated:

* numerous `unknown` placeholders;
* open `meta: Record<string, unknown>` bags;
* highly complex generic result types;
* authoring categories mirrored as IR categories;
* HTTP resources and routes as central organization.

The current general IR fixed the most important part of that problem. It now centers on:

```text
Contract
└── Group
    ├── Schema
    ├── Operation
    ├── View
    ├── StorageMapping
    ├── Workflow
    ├── Policy
    ├── Event
    └── nested Group
```

So we should reuse the archived **authoring/compiler/ref pattern**, but not its old semantic taxonomy.

---

# Can Python refs be as safe as TypeScript refs?

## Ref-kind safety: yes

Python generics can strongly distinguish ref kinds:

```python
class SchemaRef[TModel]: ...
class FieldRef[TValue]: ...
class OperationRef[TInput, TOutput]: ...
class EventRef[TPayload]: ...
class PolicyRef: ...
class StorageRef[TModel]: ...
class ViewRef: ...
class WorkflowRef: ...
class WorkflowStepRef: ...
```

Then APIs can require the correct kind:

```python
def storage(
    schema: SchemaRef[TModel],
    ...
) -> StorageRef[TModel]:
    ...

def emit(
    event: EventRef[TPayload],
) -> EventEffect:
    ...

def operation_step(
    operation: OperationRef[object, object],
) -> WorkflowStepRef:
    ...
```

Passing an `EventRef` where a `SchemaRef` is required becomes a static type error.

Passing an `OperationRef` where a workflow transition expects a `WorkflowStepRef` becomes a static type error.

## Field-name safety needs a deliberate design

TypeScript is better at deriving field-key unions directly from object literal types. That is how the existing `.pick({ email: true })` API rejects unknown properties at compile time.

Python cannot automatically turn arbitrary Pydantic model field names into a `Literal["id", "email", ...]` type without generated stubs or a type-checker plugin.

But we can avoid raw string selectors.

### Typed selector lambdas

```python
class UserModel(cp.Model):
    id: UUID
    email: EmailStr
    display_name: str
    password_hash: str


User = users.schema(UserModel)

UserRead = User.pick(
    "UserRead",
    lambda field: (
        field.id,
        field.email,
        field.display_name,
    ),
)

UserPatch = UserRead.partial("UserPatch")
```

A strict type checker understands `field` as `UserModel`.

This produces an editor error:

```python
lambda field: field.emial
#                    ^ unknown attribute
```

At runtime, the compiler invokes the selector with a restricted field-selector proxy. Attribute access produces `FieldRef` objects rather than model values.

The proxy permits only:

* declared field access;
* tuples of field accesses;
* explicitly supported selector composition.

Unknown fields are also rejected at runtime.

This gives two levels of protection:

```text
editor/type-checker error
+
author-compiler validation error
```

A later `.pyi` generator or Pyright/mypy plugin could support:

```python
User.fields.email
User.fields.id
```

but the selector-lambda API works without requiring generated code before the contract can be authored.

---

# Pydantic’s role in schema authoring

Pydantic should define author-facing schema shapes and validate their declarations.

It should not become the final IR.

## Reusable property definitions

Python and `Annotated` can preserve the “define once, reuse many times” behavior.

```python
from typing import Annotated
from uuid import UUID

from pydantic import EmailStr

import codepotg_author as cp


CommonId = Annotated[
    UUID,
    cp.field(
        format="uuid",
        readonly=True,
    ),
]

Email = Annotated[
    EmailStr,
    cp.field(
        min_length=3,
    ),
]
```

`Annotated` keeps the underlying type visible to static type checkers while attaching metadata for Pydantic and the Codepot author compiler. ([Python documentation][3])

Reuse becomes ordinary Python:

```python
class UserModel(cp.Model):
    id: CommonId
    email: Email


class OrganisationModel(cp.Model):
    id: CommonId
    owner_email: Email
```

There can also be explicit property refs:

```python
common = author.properties("common")

common_id = common.property(
    "id",
    UUID,
    format="uuid",
    readonly=True,
)

email = common.property(
    "email",
    EmailStr,
    min_length=3,
)
```

Then those refs can be attached through `Annotated`:

```python
Id = Annotated[UUID, common_id]
UserEmail = Annotated[EmailStr, email]
```

This preserves:

* type information;
* property identity;
* constraints;
* provenance;
* reuse;
* compiler ref resolution.

## Enums

Use Python enums as authoring input:

```python
from enum import StrEnum


class UserRole(StrEnum):
    ADMIN = "admin"
    ORGANISER = "organiser"
    CUSTOMER = "customer"


UserRoleSchema = users.enum(UserRole)
```

The author compiler produces one `SchemaKind.ENUM` schema. The current IR already defines structural enum schemas and requires non-empty enum values.

No template should receive the Python enum class.

---

# Proposed concise Python authoring model

```python
import codepotg_author as cp


author = cp.Author(
    id="identity",
    name="Identity",
    version="1.0.0",
)

users = author.group(
    "users",
    path=("identity", "users"),
)
```

## Schemas

```python
class UserModel(cp.Model):
    id: CommonId
    email: Email
    display_name: Annotated[
        str,
        cp.field(min_length=2, max_length=120),
    ]
    role: UserRole
    password_hash: Annotated[
        str,
        cp.field(sensitive=True),
    ]


User = users.schema(UserModel)

UserCreate = User.pick(
    "UserCreate",
    lambda field: (
        field.email,
        field.display_name,
        field.role,
    ),
)

UserRead = User.omit(
    "UserRead",
    lambda field: field.password_hash,
)

UserPatch = UserCreate.partial("UserPatch")
```

These compile into ordinary structural `Schema` and `SchemaField` objects. The final IR does not introduce model, DTO, request, or response schema kinds. The current IR supports primitive, literal, enum, object, array, map, tuple, union, intersection, alias, and unknown shapes.

## Storage mappings

Most mappings should use sensible defaults:

```python
UserStorage = users.storage(
    "UserStorage",
    schema=User,
    source="users",
)
```

The compiler can infer one column per schema field.

Only exceptions need authoring:

```python
UserStorage = (
    users.storage(
        "UserStorage",
        schema=User,
        source="users",
    )
    .primary_key(
        User.field(lambda field: field.id),
    )
    .configure(
        cp.column(
            User.field(lambda field: field.id),
            generated="uuid",
        ),
        cp.column(
            User.field(lambda field: field.email),
            indexed=True,
            unique=True,
        ),
    )
)
```

This compiles into:

* `StorageMapping`;
* `StorageFieldMapping`;
* `primary_key`;
* indexes.

Those are already explicit core IR concepts.

The author layer should never return a SQLAlchemy, TypeORM, Django, or Prisma object.

## Policies

```python
admin = users.policy(
    "Admin",
    roles=("admin",),
)

owner_or_admin = users.policy(
    "OwnerOrAdmin",
    any_of=(
        cp.condition.role("admin"),
        cp.condition.same(
            cp.context("actor.id"),
            cp.input("user_id"),
        ),
    ),
)
```

The condition builders should produce a rigid, approved policy declaration model. They must not accept arbitrary Python lambdas as semantic policy expressions unless the IR explicitly defines an expression model.

## Events

```python
UserCreated = users.event(
    "UserCreated",
    payload=UserRead,
)
```

The variable is an `EventRef[UserRead]`, not an event object embedded into every operation.

## Operations and facets

```python
create_user = users.operation(
    "createUser",
    inputs=(
        cp.input.body(UserCreate),
    ),
    outputs=(
        cp.output("created", UserRead),
    ),
    failures=(
        cp.failure(
            "email_exists",
            message="A user with this email already exists.",
        ),
    ),
    effects=cp.effects(
        emits=(UserCreated,),
    ),
    facets=cp.facets(
        http=cp.http.post("/users"),
        access=cp.access.uses(admin),
    ),
)
```

This directly matches the current IR shape:

```text
Operation
├── inputs
├── outputs
├── failures
├── effects
└── facets
```

The known operation facets currently include HTTP, access, trigger, execution, and events.

Authoring helpers such as:

```python
users.query(...)
users.command(...)
users.listener(...)
users.scheduled(...)
```

can exist, but they are convenience constructors for `Operation`.

They must not create new IR roots named query, command, listener, or job.

## Views and parts

The current IR already supports nested view parts:

```python
users_page = users.view(
    "UsersPage",
    schema=UserRead.array(),
)

users_table = users_page.part(
    "UsersTable",
    schema=UserRead.array(),
)

create_button = users_page.part(
    "CreateUserButton",
)

create_button.trigger(
    "submit",
    operation=create_user,
    payload=UserCreate,
)
```

This compiles into `View.parts` and `ViewTrigger`, not framework components.

A pack can later interpret that view as:

* a React page;
* a Flutter screen;
* a terminal presentation;
* documentation;
* a form;
* a test scenario.

The IR remains presentation-intent-oriented rather than framework-oriented.

## Workflows

```python
provision_user = users.workflow(
    "ProvisionUser",
    input=UserCreate,
    output=UserRead,
)

create = provision_user.operation_step(
    "create",
    operation=create_user,
)

notify = provision_user.operation_step(
    "notify",
    operation=send_welcome_email,
)

complete = provision_user.end_step("complete")

create.then(notify)
notify.then(complete)

create.compensate(
    delete_user,
    retry_attempts=2,
)
```

Each builder call returns a typed `WorkflowStepRef`.

Therefore:

```python
create.then(UserCreated)
```

is a static kind error because `then()` expects `WorkflowStepRef`, not `EventRef`.

The compiled IR already distinguishes operation, decision, parallel, wait, and end steps, along with transitions and compensation.

---

# The Python ref engine

The ref engine should be the center of `codepotg-author`.

## Ref model

```python
@dataclass(frozen=True, slots=True)
class Ref[T]:
    id: SemanticId
    kind: RefKind
    author_id: str
```

Public wrappers provide kind safety:

```python
SchemaRef[TModel]
FieldRef[TValue]
OperationRef[TInput, TOutput]
EventRef[TPayload]
StorageRef[TModel]
PolicyRef
ViewRef
WorkflowRef
WorkflowStepRef
```

## Ref usage is separate from ref identity

```python
UserRead
UserRead.optional()
UserRead.nullable()
UserRead.array()
```

These methods return immutable `SchemaUsage`, not a modified `SchemaRef`.

That follows the strongest part of the existing implementation: one stable identity, many context-specific usages.

## No process-global registry

The current Node implementation has a module-level `schemaDefinitionsByRefId` map used for projection lookup. That works operationally, but it is exactly what the v2 Python author package should avoid.

Instead:

```text
Author
├── declaration registry
├── ref registry
├── source-location registry
└── diagnostics
```

Every ref belongs to one explicit `Author` session.

This supports:

* multiple contracts in one process;
* parallel tests;
* deterministic compilation;
* no import-order state;
* no cleanup function;
* no cross-contract ref leakage.

## Forward refs

Most refs should be returned by definitions:

```python
UserCreated = users.event(...)
```

When a real forward reference is required:

```python
notify = provision_user.declare_step("notify")

create = provision_user.operation_step(
    "create",
    operation=create_user,
)

create.then(notify)

provision_user.define_step(
    notify,
    operation=send_welcome_email,
)
```

The forward ref already has a kind. Compilation verifies that it was eventually defined.

No user writes a raw `$ref`.

---

# Compiler stages

The author compiler should behave more like a linker than a serializer.

```text
1. Collect authoring declarations
2. Freeze registries
3. Assign deterministic semantic IDs
4. Resolve all typed refs
5. Validate ref kinds
6. Expand property reuse
7. Expand schema projections
8. Expand authoring convenience patterns
9. Compile groups and schemas
10. Compile storage mappings
11. Compile policies and events
12. Compile operations and facets
13. Compile views and nested parts
14. Compile workflows and transitions
15. Construct immutable core Contract
16. Run codepotg.ir.validate_contract
17. Produce canonical IR digest
18. Optionally serialize JSON/YAML
```

Errors should include:

* declaration source;
* expected ref kind;
* actual ref kind;
* missing target;
* duplicate target;
* referencing declaration;
* suggestions where safe.

The old archive’s multi-pass compiler was directionally correct.

---

# Is the current Codepot IR convertible to JSON?

## Yes, structurally

The current IR consists of frozen dataclasses, enums, tuples, semantic IDs, scalar values, and bounded frozen objects. For example, `Contract` and `Group` are immutable dataclasses, and references between semantic objects are represented by `SemanticId` rather than recursive object pointers.

That makes it naturally serializable.

However, in the public core APIs I inspected, I found the IR façade and validation API but not yet a complete public canonical JSON round-trip codec.

We should add one deliberately rather than use generic `dataclasses.asdict()`.

## Canonical transport document

```json
{
  "$schema": "https://codepot.dev/schema/ir/2.0.json",
  "format": "codepot-ir",
  "irVersion": "2.0.0-alpha.1",
  "behaviorVersions": {
    "naming": 1,
    "semantics": 1
  },
  "contract": {
    "id": "identity",
    "name": "Identity",
    "version": "1.0.0",
    "groups": [
      {
        "id": "identity.users",
        "name": "Users",
        "path": ["identity", "users"],
        "schemas": [
          {
            "id": "identity.users.schema.User",
            "name": "User",
            "kind": "object",
            "fields": [
              {
                "id": "identity.users.schema.User.field.email",
                "name": "email",
                "type": {
                  "kind": "primitive",
                  "name": "string"
                },
                "required": true,
                "nullable": false
              }
            ]
          }
        ],
        "operations": [
          {
            "id": "identity.users.operation.createUser",
            "name": "createUser",
            "inputs": [
              {
                "name": "body",
                "schema": {
                  "$ref": "identity.users.schema.UserCreate"
                },
                "required": true
              }
            ],
            "outputs": [
              {
                "name": "created",
                "schema": {
                  "$ref": "identity.users.schema.UserRead"
                }
              }
            ],
            "facets": {
              "http": {
                "method": "POST",
                "path": "/users"
              }
            }
          }
        ]
      }
    ]
  }
}
```

The in-memory IR may store a reference as `SemanticId`. The transport format can represent it explicitly as:

```json
{"$ref": "identity.users.schema.UserRead"}
```

The archived rewrite got this distinction right: authoring refs used internal ID/kind/key values, while compiled JSON/YAML used portable `$ref` structures.

## Required codec API

```python
from codepotg.ir.codec import (
    contract_from_document,
    contract_from_json,
    contract_from_yaml,
    contract_to_document,
    contract_to_json,
    contract_to_yaml,
)
```

Required guarantees:

```python
decoded = contract_from_json(contract_to_json(contract))

assert decoded == contract
```

The codec must provide:

* canonical key ordering;
* explicit IR version;
* behavior versions;
* stable enum values;
* canonical semantic IDs;
* no Python class names;
* no object addresses;
* no authoring helpers;
* no Pydantic models;
* no target-language values;
* strict unknown-field handling;
* version migration diagnostics;
* ref resolution;
* core validation after loading.

## JSON and YAML roles

```text
Canonical compact JSON:
hashing, transport, caching, signatures

Pretty JSON:
debugging, reviews, golden fixtures

YAML:
human inspection and optional exchange

JSONL:
large-contract indexing/cache representation
```

Canonical identity should be based on canonical JSON, not YAML formatting.

---

# Can serialized IR be used as input like OpenAPI?

Yes.

The complete input architecture should become:

```text
Python codepotg-author
        ────────────────┐
OpenAPI source adapter ─┤
Codepot IR JSON/YAML ───┼──> immutable Contract
Native Codepot language ┤
Future TS author SDK ───┘
```

A serialized Codepot IR file should require no inference. It is already compiled semantics.

For example:

```bash
codepotg generate contract.codepot.json
```

or:

```python
contract = contract_from_json(path.read_text())
result = codepotg.generate(contract, ...)
```

If the runtime requires all file sources to use adapters, provide an official minimal IR adapter:

```text
codepotg-ir
```

Its only responsibilities would be:

* decode canonical JSON/YAML;
* validate the IR version;
* resolve `$ref` values;
* reconstruct immutable core IR;
* call core validation;
* return the contract and digest.

It would not infer or add semantics.

OpenAPI remains different:

```text
OpenAPI document
→ interpretation and normalization
→ Codepot IR
```

Canonical IR input is:

```text
Codepot IR document
→ strict decoding
→ Codepot IR
```

---

# What “normal Tuesday” authoring requires

The author must not manually manage:

* `$ref` strings;
* component locations;
* group arrays;
* operation registries;
* schema duplication;
* field duplication;
* storage field IDs;
* view trigger IDs;
* workflow transition names;
* JSON output assembly;
* ordering;
* digest calculation.

A normal module should look like:

```python
def define_users(author: cp.Author) -> cp.GroupRef:
    users = author.group("users")

    User = users.schema(UserModel)

    UserRead = User.omit(
        "UserRead",
        lambda field: field.password_hash,
    )

    UserCreated = users.event(
        "UserCreated",
        payload=UserRead,
    )

    create_user = users.operation(
        "createUser",
        inputs=(cp.input.body(UserCreate),),
        outputs=(cp.output("created", UserRead),),
        effects=cp.effects(emits=(UserCreated,)),
        facets=cp.facets(
            http=cp.http.post("/users"),
        ),
    )

    users.view(
        "CreateUser",
        schema=UserCreate,
    ).trigger(
        "submit",
        operation=create_user,
    )

    return users.ref
```

Composition remains explicit:

```python
author = cp.Author(...)

define_identity(author)
define_users(author)
define_orders(author)

result = author.compile()
```

No package scanning and no import-time global registration.

---

# Error detection layers

A well-designed `codepotg-author` gives five safety layers.

| Layer                      | Catches                                                                                            |
| -------------------------- | -------------------------------------------------------------------------------------------------- |
| Static checker             | Wrong ref kinds, invalid method arguments, unknown Pydantic fields, incorrect builder use          |
| Pydantic author validation | Invalid constraints, incorrect option values, malformed declaration structures                     |
| Ref linker                 | Missing targets, duplicate IDs, wrong-kind refs, unresolved forwards, cross-author refs            |
| Core IR validator          | Invalid semantic relationships, missing schemas, invalid workflow transitions, incompatible facets |
| Canonical codec            | Invalid IR versions, unknown fields, malformed `$ref`, non-round-trippable data                    |

No single layer should be expected to do everything.

---

# Final architectural decision

The attached suggestion correctly recognizes that OpenAPI should no longer own Codepot authoring. But its separate Contract Graph and direct target compilers would fork the architecture. 

The stronger design is:

```text
Pydantic + Python authoring
        ↓
typed declarations and refs
        ↓
multi-pass author compiler
        ↓
existing general Codepot IR
        ↓
canonical Codepot IR JSON/YAML
        ↓
root-first planner and selectors
        ↓
packs, target adapters, Jinja, writer
```

The key principle should be:

> **Define once in concise typed Python, reuse through typed refs, compile into verbose rigid portable IR, and let every generator consume exactly that same IR.**

That preserves the direction we chose while recovering the feature that made `codepot-openapi` genuinely pleasant: users express intent once, and the compiler performs the difficult joining, resolving, expanding, validating, and serialization.

[1]: https://typing.python.org/en/latest/spec/dataclasses.html "https://typing.python.org/en/latest/spec/dataclasses.html"
[2]: https://docs.pydantic.dev/2.6/integrations/mypy/ "https://docs.pydantic.dev/2.6/integrations/mypy/"
[3]: https://docs.python.org/3/library/typing.html?highlight=dataclass_transform "https://docs.python.org/3/library/typing.html?highlight=dataclass_transform"
