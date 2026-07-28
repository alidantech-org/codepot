## Overall evaluation

The design has a strong semantic foundation:

* One closed `dryv.ir.Contract`
* Explicit author sessions
* Immutable typed references
* Deterministic linking
* Structural schemas instead of ORM entities
* Explicit operations, storage, views, presentations and workflows
* No private author-only semantic graph
* No generation or template behavior inside `dryv-author`

However, the current plan is **not yet a fully strongly typed flowing builder design**. It describes many typed objects, but it does not completely define how those objects flow through Python builders without falling back to dynamic attributes, string selectors, dictionaries or runtime-only validation.

The old TypeScript design demonstrates the right authoring experience:

```text
define something
→ receive typed references
→ feed those references into another builder
→ receive more typed references
→ continue building
```

That proven flow should be borrowed. The TypeScript implementation details should not be copied directly because TypeScript can infer object-map keys more easily than Python.

---

# 1. The most important improvement: define the type flow

The plan currently lists types such as:

```text
SchemaRef[T]
FieldRef[T]
OperationRef[TInput, TOutput]
EventRef[TPayload]
```

That is good, but the design must also describe exactly what every builder accepts and returns.

For example:

```text
property builder
    → PropertyRef[T]

schema builder + PropertyRef[T]
    → FieldRef[T]

schema definition + FieldRef values
    → SchemaRef[TModel]

schema derivation + FieldRef values
    → SchemaRef[TDerived]

operation builder + SchemaRef[TInput] + SchemaRef[TOutput]
    → OperationRef[TInput, TOutput]

value-source builder + OperationRef + FieldRef
    → ValueSourceRef[TValue]

view builder + SchemaRef + OperationRef + ValueSourceRef
    → ViewRef

presentation builder + ViewRef
    → PresentationRef
```

This flow should be written as a contract for the author API, not merely implied.

Each semantic builder must answer:

1. What typed values does it accept?
2. What typed handle or reference does it return?
3. Which later builders accept that result?
4. Which invalid combinations are rejected statically?
5. Which remaining conditions are checked by the linker?

Without this, the implementation can become a collection of individually typed classes that still communicate through strings and dictionaries.

---

# 2. Borrow the old builder flow, not its object-map mechanics

The old design succeeds because references naturally move forward:

```typescript
const user = schemas.entity(...);

user.ref.fields.role
user.ref.models.public
dtos.ref.UserResponse
policies.ref.protected
errors.ref.unauthorized
```

The Python design should preserve this experience conceptually:

```python
User
User.fields.role
User.models.public
protected_policy
unauthorized_failure
```

But Python cannot automatically infer arbitrary keys from dictionaries as strongly as TypeScript can.

This TypeScript pattern:

```typescript
const models = user.models({
  public: ...,
  create: ...,
  patch: ...,
});
```

automatically gives TypeScript a typed object with:

```typescript
models.public
models.create
models.patch
```

A normal Python dictionary cannot provide equivalent strict attribute typing:

```python
models = {
    "public": ...,
    "create": ...,
}
```

Therefore, the Python plan must explicitly choose how typed namespaces are produced.

## Suitable approaches

### Direct typed results

Every declaration is assigned to a Python variable:

```python
UserPublic = User.derive.pick(
    "UserPublic",
    User.fields.id,
    User.fields.name,
    User.fields.role,
)

UserCreate = User.derive.omit(
    "UserCreate",
    User.fields.id,
)

UserPatch = User.derive.partial(
    "UserPatch",
    UserCreate,
)
```

This is the easiest form for Pyright and mypy to understand because every returned value has a concrete generic type.

### Typed declaration classes

A class may define a typed namespace where Python can inspect declared attributes:

```python
class UserModels(cp.SchemaModels):
    public = User.derive.pick(...)
    create = User.derive.omit(...)
    patch = User.derive.partial(...)
```

The exact syntax still needs design, but the important point is that the namespace must have statically declared members. It cannot be an arbitrary dictionary pretending to be strongly typed.

## What must be avoided

Do not promise that this is strongly typed:

```python
User.ref.models.public
```

unless the implementation has a real mechanism that makes `public` visible to Pyright and mypy.

Dynamic `__getattr__` may make it work at runtime, but it does not make it genuinely strongly typed.

---

# 3. Use handles for building and refs for relationships

The plan currently moves between the ideas of a `SchemaAuthor`, `SchemaRef`, declaration and handle. These should be separated clearly.

A clean model is:

```text
SchemaBuilder[T]
    mutable only during declaration construction

SchemaDefinition[T]
    completed immutable author declaration

SchemaRef[T]
    immutable semantic identity used by other declarations

SchemaUse[T]
    required/optional/nullable/array use of the reference
```

For example:

```python
User: SchemaDefinition[UserModel]

User.ref
User.fields.email
User.derive
User.storage
```

Relationships should receive refs or a shared ref protocol:

```python
create_user.output(User.ref)
event.payload(User.ref)
```

For convenience, a completed definition may satisfy a protocol such as:

```python
RefLike[SchemaRef[T]]
```

That would allow:

```python
create_user.output(User)
```

without confusing the internal distinction between the author declaration and its semantic reference.

The compiler should still normalize it to:

```python
User.ref
```

This gives the clean builder flow without collapsing definitions, references and uses into one mutable object.

---

# 4. Separate identity strings from semantic strings

The goal should not be “no strings anywhere.” Names, descriptions and route paths are naturally text.

The correct rule is:

> Strings may introduce identity or human-readable information, but strings must not establish semantic relationships when a typed reference can do so.

## Reasonable strings

These are legitimate:

```python
author.group("accounts")
schemas.entity("User")
operations.command("createUser")
http.get("/users/{id}")
view.title("Manage users")
```

They declare names, paths or documentation.

## Strings that should not be accepted

These should be refs or typed values:

```python
operation.output("accounts.User")
schema.pick("id", "email")
event.payload("User")
view.trigger("createUser")
field.reference("users.id")
operation.kind("command")
facet("http")
method("GET")
guidance.category("security")
presentation.channel("mobile")
```

They should become:

```python
operation.output(User)
schema.pick(User.fields.id, User.fields.email)
event.payload(User)
view.trigger(create_user)
field.references(User.fields.id)
operation.kind(OperationKind.COMMAND)
http.method(HttpMethod.GET)
guidance.security(...)
presentation.channel(PresentationChannel.MOBILE)
```

The author compiler may serialize these as strings in canonical JSON, but the Python author should not manually connect the system using those strings.

---

# 5. Typed field access is the unresolved core problem

The plan says:

```python
User.pick("UserRead", lambda f: (f.id, f.email, f.display_name))
```

This removes explicit field-name strings, but it does not automatically guarantee static typing.

Python cannot naturally transform:

```python
UserModel.id: UUID
```

into:

```python
selector.id: FieldRef[UUID]
```

using ordinary generics alone.

Therefore, the design must not leave this as an assumed capability.

The complete plan must select one supported mechanism:

* Explicit typed field-ref variables
* Typed declaration classes
* Generated static stubs
* A deliberately implemented checker integration
* Another concrete mechanism that Pyright and mypy can actually verify

The current statement that a mypy/Pyright plugin or generated `.pyi` files are merely future optimizations is too weak. Either the public API avoids needing them, or the required static-typing infrastructure must be part of the complete implementation.

Runtime proxy lambdas alone are not enough to claim strong static typing.

---

# 6. Builders should expose only valid next operations

The older design uses nested builders well:

```typescript
.capability((capability) => capability.filter().sort().select())
.lifecycle((lifecycle) => lifecycle.generated().immutable())
.persistence((persistence) => persistence.stored())
```

This is better than accepting dictionaries:

```python
field(
    capabilities={
        "filter": True,
        "sort": True,
        "select": True,
    }
)
```

Dryv should borrow this nested builder style.

For example:

```python
field(UserName)
    .required()
    .capability(
        lambda capability:
            capability.filter().sort().select()
    )
    .visibility(
        lambda visibility:
            visibility.public()
    )
```

The callback receives a narrow typed builder. It cannot accidentally call persistence methods inside the visibility builder.

This creates a strongly typed flow:

```text
FieldBuilder[T]
  ├── capability(CapabilityBuilder)
  ├── lifecycle(LifecycleBuilder)
  ├── visibility(VisibilityBuilder)
  └── storage(StorageFieldBuilder)
```

Each nested builder should use typed methods and enums, not arbitrary keyword dictionaries.

## Typestate where it provides real value

Some builders should use state-specific protocols or generic state markers.

For example:

```text
OperationBuilder[OutputMissing]
    .output(...)
        ↓
OperationBuilder[OutputDefined]
```

Only the completed state should expose `.define()`.

Similar constraints can prevent:

* Defining two operation bodies
* Marking a field both required and optional
* Declaring more than one HTTP path binding for one input
* Completing an unresolved workflow step
* Creating a value source without a value field
* Creating a presentation placement without a view

Not every tiny rule needs to become a generic parameter, but major invalid builder states should be unrepresentable where practical.

---

# 7. Field capabilities must become typed builders

The current plan describes field capabilities textually:

```text
initialization eligibility
mutation eligibility
visibility/sensitivity
query operators
sortable/selectable capability
semantic reference target
```

These must become closed typed APIs.

For example:

```python
field.capability(
    lambda c: c
        .filter(FilterOperators.equal().in_values())
        .sort()
        .select()
)

field.lifecycle(
    lambda lifecycle: lifecycle
        .generated()
        .immutable()
)

field.visibility(
    lambda visibility: visibility
        .internal()
        .sensitive()
)

field.reference(User.fields.id)
```

Avoid:

```python
capability="filter"
capabilities=["filter", "sort"]
query_operators=["eq", "in"]
visibility="internal"
```

The compiled IR may use enum values, but authoring should use enum members or typed fluent methods.

---

# 8. Tags are currently the most stringly typed section

The tags document calls tags an “escape hatch.” That is dangerous if the goal is a strongly typed semantic system.

Tags can remain available, but they should not be repeatedly written as raw strings:

```python
view.tags("ui:data-table", "ui:filter:advanced")
```

A better authoring flow is to declare or resolve tag references once:

```python
ui = author.tags.namespace("ui")

data_table = ui.tag("data-table")
advanced_filter = ui.tag("filter:advanced")

view.tags(data_table, advanced_filter)
```

Then:

```text
TagRef
```

flows through authoring, compilation and template context.

The canonical IR may still contain:

```json
"ui:data-table"
```

but typos and malformed namespaces are caught when the tag is declared rather than silently scattered throughout the authoring project.

Known semantics must never be represented with tags. For example, these should remain typed facts:

* Requiredness
* Sensitivity
* HTTP method
* Storage behavior
* Operation kind
* Presentation channel
* Query support

Also, the reserved namespace in the plan says:

```text
codepot:*
```

That should be reviewed for consistency with the Dryv naming. If the engine-owned namespace is meant to be Dryv-specific, it should be:

```text
dryv:*
```

---

# 9. Guidance categories should be builder methods

Guidance already has a promising builder shape:

```python
view.info(
    lambda i: i
        .explain("Main admin page.")
        .implement("Keep filters above the table.")
)
```

That is preferable to:

```python
view.info("explain", "Main admin page")
```

The approved categories should all become explicit typed methods:

```text
.explain(...)
.implement(...)
.warn(...)
.security(...)
.persistence(...)
.caching(...)
.testing(...)
.observability(...)
.ux(...)
.accessibility(...)
```

Guidance remains descriptive and cannot activate semantic behavior.

This avoids both arbitrary category strings and AI-like interpretation of prose. Dryv records exactly what category the author selected.

---

# 10. No inferred behavior

The plan already mostly follows this rule, but it should be stated as a compiler invariant:

Dryv Author must never infer semantic behavior from:

* Field names
* Class names
* Documentation text
* Guidance
* Tags
* Type names
* Conventional suffixes
* Pydantic validators
* Operation names

For example:

```python
email: EmailStr
```

does not automatically mean:

```text
unique storage constraint
login identity
sensitive visibility
search capability
email input control
```

Those facts must be declared explicitly.

Likewise:

```python
create_user
```

does not automatically become an HTTP POST operation.

This keeps the system deterministic and avoids AI-style guessing.

---

# 11. All outlined features must be required, not conditional

Several parts of the documents conflict with your requirement that every outlined feature must be implemented and validated.

Problematic wording includes:

* “future optimizations”
* “first usable ref engine”
* “when supported by core”
* “if core approves presentations”
* “proposed neutral semantic object”
* “implements the available subset”
* “records exact blockers”
* “may later publish the missing contracts”

That wording allows an incomplete author package to be considered successful.

The improved rule should be:

> Every concept approved in this design is part of the required finished system. Implementation may be dependency-ordered, but completion is not reached until the core IR, validation, canonical transport, selectors, template contexts and `dryv-author` builders support every approved concept.

Dependency order is still necessary:

```text
core typed semantic model
→ core validation
→ canonical transport
→ selectors and bounded contexts
→ author builders
→ author compiler
→ full cross-feature validation
```

That is not reducing scope. It is ensuring that each dependency exists before the author compiler targets it.

`ValueSource`, presentations, guidance, tags, connected field capabilities and expanded HTTP bindings must not remain declarations that always return `AUTHOR_CORE_UNSUPPORTED`. Their required core forms must be built as part of the same complete design programme.

---

# 12. The “parallel implementation rule” must change

The final document currently says that the author implementation:

* must not modify Dryv core;
* implements the available subset;
* records blockers;
* waits for a separate core lane.

That produces a knowingly incomplete `dryv-author`.

A better rule is:

* Core and author work may be implemented in separate ownership lanes.
* Core changes must land before dependent author compiler phases are considered complete.
* Every approved core gate is tracked as a required dependency.
* The complete design is accepted only when all author declarations compile into public core IR.
* No outlined feature is allowed to survive only as an unsupported declaration.

The separation of ownership is fine. The subset completion rule is not.

---

# 13. Transport ownership contains an inconsistency

The architecture document lists:

```text
dryv_author.transport.*
```

as a planned public API family.

Other documents correctly state that canonical transport belongs to `dryv`, not `dryv-author`.

The plan should choose the latter consistently:

```python
result = author.compile()
contract = result.require_contract()

dryv.ir.contract_to_json(contract)
dryv.ir.contract_to_yaml(contract)
```

`dryv-author` should not own:

```python
author.to_json()
author.to_yaml()
dryv_author.transport
```

unless it is only a transparent import alias—which would still blur package ownership unnecessarily.

Also, serialization should not be compiler phase 22. Compilation ends with the immutable contract and diagnostics. Serialization is a separate runtime action performed after compilation.

---

# 14. Separate semantic digest from authoring-build digest

The current digest includes:

* Author package version
* Pydantic behavior version
* Derivation behavior version
* Core version
* Semantic content

That creates an important ambiguity.

Two different authoring frontends may compile to the exact same Dryv contract:

```text
Python authoring ─┐
                  ├── identical Contract
Canonical YAML ───┘
```

The canonical semantic digest should be identical for both.

The design should distinguish:

```text
contract_digest
    Derived only from canonical Dryv semantic content and relevant IR behavior versions.

authoring_build_digest
    Includes dryv-author version, Pydantic interpretation version,
    author options and compiler behavior.
```

This preserves the claim that the Dryv contract is the single semantic authority while still allowing author compilation caching.

---

# 15. Internal identifiers should also be typed

This is currently proposed:

```python
class RefIdentity:
    author_id: str
    declaration_id: str
    kind: RefKind
```

`kind` is typed, but the IDs are plain strings.

Internally, use distinct immutable value types:

```text
AuthorId
DeclarationId
SemanticId
GroupId
SourceId
```

This prevents accidentally passing a declaration ID where an author ID is expected.

Canonical transport can encode them as strings. Python code should retain the distinct types.

---

# 16. Operations need a full typed builder flow

The operations document currently lists the operation structure but does not sufficiently define its builder progression.

The flow should resemble:

```text
OperationBuilder
    → inputs
    → outputs
    → failures
    → effects
    → facets
    → OperationRef
```

Every connection should use typed refs:

```python
create_user = accounts.operations.command("createUser") \
    .input(CreateUser) \
    .output(UserRead) \
    .failures(unauthorized, email_taken) \
    .emits(UserCreated) \
    .access(protected_policy) \
    .http(
        lambda http: http
            .post("/users")
            .body(CreateUser)
            .responds(UserRead, status=HttpStatus.CREATED)
    ) \
    .define()
```

This is illustrative rather than a final syntax.

Important typing rules include:

* `.input()` accepts schema uses.
* `.output()` accepts schema uses.
* `.failures()` accepts only failure refs.
* `.emits()` accepts only event refs.
* `.access()` accepts only policy refs.
* `.http()` receives only an HTTP facet builder.
* HTTP methods and statuses are enums or typed constants.
* Input bindings point to input field refs, not field names.
* Response bindings point to output refs.
* Effects cannot receive arbitrary dictionaries.

---

# 17. Views, presentations and value sources need reference-first builders

These areas currently describe semantics correctly but remain too textual.

A value source should flow from existing refs:

```text
OperationRef[ListUsersQuery, UserList]
    + output collection ref
    + FieldRef[UUID]
    + FieldRef[str]
        ↓
ValueSourceRef[UUID]
```

A view should consume refs:

```text
SchemaRef
OperationRef
FieldRef
ValueSourceRef
PolicyRef
    ↓
ViewRef
```

A presentation should consume view refs:

```text
ViewRef
Address value
Navigation relationship
PolicyRef
    ↓
PresentationRef
```

No view or presentation connection should rely on:

```python
"users.list"
"createUser"
"accounts.User"
"user-picker"
```

except as declaration names. Cross-object relationships must use the returned refs.

---

# 18. Recommended locked builder principle

The plan should adopt this as a central rule:

> Every semantic declaration returns a typed immutable handle or reference. Every later semantic declaration consumes those handles or references. Strings introduce names and human text, but never replace semantic connections.

The old Codepot design proved the usability of:

```text
builder
→ ref
→ connected builder
→ new ref
```

Dryv Author should preserve that exact experience in Python, while avoiding unsupported dynamic object-map inference.

## Final assessment

The design is semantically mature, but its typing story currently stops one level too early. It defines typed ref classes without fully defining the typed flow of every public builder.

The most important corrections are:

1. Specify all builder inputs and returned reference types.
2. Select a real mechanism for statically typed field and model access.
3. Use typed handles for all relationships instead of names.
4. Replace semantic string options with enums and narrow builders.
5. Turn tags into declared `TagRef` values at the authoring level.
6. Make all approved core gates mandatory parts of completion.
7. Remove subset, unsupported-until-later and future-optimization language.
8. Keep canonical transport exclusively in `dryv`.
9. Separate contract digest from authoring-build digest.
10. Validate the entire connected flow—from properties through presentations and workflows—not isolated feature examples.

The correct character of `dryv-author` is not a loose Python configuration API. It is a **typed semantic construction system where every completed declaration becomes the input of the next valid builder**.


This is a better direction. It removes hidden behavior while preserving powerful schema derivation.

The key architectural change is:

```text
Schema structure
≠
Field capabilities
≠
Schema derivations
≠
Field mappings
```

These should be connected, but none should silently define the others.

## 1. Keep the base schema purely structural

A schema should initially describe only its shape:

```python
User = accounts.schemas.object(
    "User",
    lambda f: {
        "id": f.uuid().required(),
        "first_name": f.string().required(),
        "last_name": f.string().required(),
        "email": f.email().required(),
        "password_hash": f.string().required(),
    },
)
```

At this stage, Dryv knows:

* Field names
* Field types
* Requiredness
* Nullability
* Defaults
* Structural relationships
* Constraints

It should not yet decide:

* Which fields are public
* Which fields appear in create inputs
* Which fields are queryable
* Which fields are persisted
* Which fields are mutable
* Which fields appear in forms

That prevents structural schemas from becoming overloaded entities.

---

## 2. Define capabilities separately from schema construction

The schema can expose a capability builder after it exists:

```python
User.field_capabilities(
    lambda fields: fields
        .field(
            fields.id,
            lambda capability: capability
                .expose("public")
                .selectable()
                .filterable()
                .generated()
                .immutable(),
        )
        .field(
            fields.email,
            lambda capability: capability
                .expose("internal")
                .filterable()
                .sensitive(),
        )
        .field(
            fields.password_hash,
            lambda capability: capability
                .sensitive()
                .hidden()
                .immutable(),
        )
)
```

The exact fluent syntax can be polished later, but the separation is correct.

Capabilities become **facts about fields**, not instructions to immediately generate another schema.

For example:

```text
FieldCapability
├── exposure labels
├── visibility facts
├── mutation facts
├── initialization facts
├── query capabilities
├── selection capabilities
├── sensitivity
├── lifecycle
└── namespaced tags
```

Most importantly:

> Capabilities describe what a field supports. They do not automatically create DTOs, endpoints, forms, storage columns or projections.

---

## 3. Remove automatic named derivations

I agree that Dryv should not automatically create fixed shapes such as:

```text
UserCreate
UserUpdate
UserRead
UserPublic
UserQuery
```

Those names and meanings are application decisions.

The previous approach risks assuming that:

* Every application has one public representation.
* Every update schema follows the same rules.
* Create always excludes generated fields.
* Read always contains all visible fields.
* Query always contains every filterable field.

Those assumptions become rigid as applications grow.

Instead, every derived schema should be explicitly declared:

```python
UserPublic = User.derive(
    "UserPublic",
    lambda derivation: derivation
        .include(
            lambda fields: fields.capability("exposure:public")
        )
)
```

Or explicitly:

```python
UserPublic = User.pick(
    "UserPublic",
    lambda f: (
        f.id,
        f.first_name,
        f.last_name,
        f.email,
    ),
)
```

The user decides that `UserPublic` exists and what it means.

Dryv only executes the declared derivation deterministically.

---

## 4. Preserve capability-based derivation

Removing automatic derivation should not remove derivation by capabilities.

The stronger model is:

```text
Capabilities provide selectable facts.
Derivation builders explicitly choose how to use those facts.
```

For example:

```python
UserCreate = User.derive(
    "UserCreate",
    lambda d: d
        .include(lambda f: f.capability("initialization:accepted"))
        .exclude(lambda f: f.capability("lifecycle:generated"))
)
```

A more typed API would avoid string capability names:

```python
UserCreate = User.derive(
    "UserCreate",
    lambda d: d
        .include(lambda f: f.initialization.accepted)
        .exclude(lambda f: f.lifecycle.generated)
)
```

Or:

```python
UserCreate = User.derive(
    "UserCreate",
    lambda d: d
        .where(
            lambda field: field.capabilities.initialization.accepted
        )
        .where_not(
            lambda field: field.capabilities.lifecycle.generated
        )
)
```

The important distinction is that the derivation is still explicitly authored.

Dryv does not see capabilities and independently decide to create `UserCreate`.

---

## 5. Support both explicit refs and typed filters

The derivation builder should support several composable selection mechanisms.

### Explicit picks

```python
UserRead = User.pick(
    "UserRead",
    lambda f: (
        f.id,
        f.first_name,
        f.last_name,
        f.email,
    ),
)
```

### Explicit omissions

```python
UserWithoutSecrets = User.omit(
    "UserWithoutSecrets",
    lambda f: (
        f.password_hash,
        f.password_reset_token,
    ),
)
```

### Capability filters

```python
UserPublic = User.derive(
    "UserPublic",
    lambda d: d.include(
        lambda f: f.capabilities.exposure.public
    ),
)
```

### Tag filters

```python
UserSearchResult = User.derive(
    "UserSearchResult",
    lambda d: d.include(
        lambda f: f.tags.contains(search.result)
    ),
)
```

### Combined conditions

```python
UserListItem = User.derive(
    "UserListItem",
    lambda d: d
        .include(lambda f: f.capabilities.exposure.public)
        .exclude(lambda f: f.tags.contains(ui.detail_only))
        .include_fields(lambda f: (f.id,))
)
```

### Structural modification

```python
UserPatch = User.derive(
    "UserPatch",
    lambda d: d
        .pick(lambda f: (f.first_name, f.last_name, f.email))
        .optional()
)
```

These are all explicit derivations with deterministic provenance.

---

## 6. The lambda selector should remain central

I agree that this is a good authoring shape:

```python
User.pick(
    "UserRead",
    lambda f: (
        f.id,
        f.email,
        f.display_name,
    ),
)
```

It is much cleaner than:

```python
User.pick("UserRead", "id", "email", "display_name")
```

The lambda gives Dryv a bounded typed field namespace.

It also makes refactoring safer:

```python
lambda f: f.display_name
```

is connected to a field ref, while:

```python
"display_name"
```

is only text.

The builder should support both singular and tuple selections naturally:

```python
User.pick("UserId", lambda f: f.id)

User.pick(
    "UserSummary",
    lambda f: (f.id, f.display_name),
)
```

The lambda is not the problem. The implementation must ensure that the selector object exposes real typed field refs and does not merely fake attributes through unrestricted `__getattr__`.

---

## 7. Mappings should be a first-class derivation feature

Your full-name example shows why `pick`, `omit` and `partial` alone are insufficient.

Suppose the canonical schema has:

```text
User
├── first_name
└── last_name
```

But an external input uses:

```text
CreateUserInput
└── full_name
```

A derived schema needs to support shape transformation rather than only field filtering.

For example:

```python
CreateUserInput = User.derive(
    "CreateUserInput",
    lambda d: d
        .omit(lambda f: (f.first_name, f.last_name))
        .add(
            "full_name",
            cp.string().required(),
        )
        .map(
            target=lambda f: (f.first_name, f.last_name),
            source=lambda f: f.full_name,
            using=split_full_name,
        )
)
```

However, a critical boundary is needed:

### The mapping declaration is semantic

Dryv may describe:

* Source fields
* Target fields
* Mapping direction
* Mapping identifier
* Input and output types
* Whether it is reversible
* Whether it is lossy
* Mapping guidance

### The mapping implementation is runtime-specific

Dryv should not embed arbitrary Python functions into the contract.

So instead of placing `split_full_name` itself in the IR, authoring could produce a typed mapping ref:

```python
SplitFullName = mappings.define(
    "splitFullName",
    source=FullName,
    output=NameParts,
)
```

Then:

```python
CreateUserInput = User.derive(
    "CreateUserInput",
    lambda d: d
        .remove(lambda f: (f.first_name, f.last_name))
        .add(lambda fields: fields.full_name(FullName))
        .map(
            source=lambda f: f.full_name,
            target=lambda f: (f.first_name, f.last_name),
            using=SplitFullName,
        )
)
```

This allows packs to generate or bind the actual mapping implementation without putting Python callables in canonical IR.

---

## 8. Distinguish field transformation operations

The derivation builder should explicitly support several different operations instead of treating all of them as generic “mapping.”

```text
Selection
    pick, omit, include, exclude

Usage modification
    required, optional, nullable, array

Field transformation
    rename, retype, constrain, annotate

Shape construction
    add, replace, extend

Semantic mapping
    one-to-one
    one-to-many
    many-to-one
    many-to-many
```

Examples:

### Rename

```python
UserOutput = User.derive(
    "UserOutput",
    lambda d: d.rename(
        lambda f: f.display_name,
        "name",
    ),
)
```

### Change requiredness

```python
UserPatch = User.derive(
    "UserPatch",
    lambda d: d
        .pick(lambda f: (f.first_name, f.last_name))
        .modify(
            lambda f: f.all(),
            lambda field: field.optional(),
        )
)
```

### Add a derived field

```python
UserProfile = User.derive(
    "UserProfile",
    lambda d: d
        .pick(lambda f: (f.id, f.first_name, f.last_name))
        .add(
            "display_name",
            DisplayName,
            from_fields=lambda f: (f.first_name, f.last_name),
            using=BuildDisplayName,
        )
)
```

### Split one field into several

```python
StoredUser = CreateUserInput.derive(
    "StoredUser",
    lambda d: d
        .remove(lambda f: f.full_name)
        .add_fields(
            lambda fields: (
                fields.first_name(FirstName),
                fields.last_name(LastName),
            )
        )
        .map(
            source=lambda f: f.full_name,
            target=lambda f: (f.first_name, f.last_name),
            using=SplitFullName,
        )
)
```

This gives derivations real expressive power without hidden guessing.

---

## 9. Global derivation rules are a strong idea

Reusable session-level derivation rules solve repeated policy without making the engine automatic.

For example:

```python
public_schema = author.derivation_rules.define(
    "publicSchema",
    lambda rule: rule
        .include(lambda f: f.capabilities.exposure.public)
        .exclude(lambda f: f.capabilities.sensitivity.secret)
)
```

Then:

```python
UserPublic = User.derive(
    "UserPublic",
    lambda d: d.apply(public_schema),
)

OrderPublic = Order.derive(
    "OrderPublic",
    lambda d: d.apply(public_schema),
)
```

This is still explicit because the author says:

```python
d.apply(public_schema)
```

The rule does not automatically run against every schema.

Rules can also be composed:

```python
public_mutable_input = author.derivation_rules.compose(
    "publicMutableInput",
    public_fields,
    mutable_fields,
    accepted_input_fields,
)
```

Then:

```python
UserSelfUpdate = User.derive(
    "UserSelfUpdate",
    lambda d: d
        .apply(public_mutable_input)
        .omit(lambda f: f.id)
)
```

This provides reuse without hidden generation.

---

## 10. Rules should themselves be typed references

A reusable rule should return something like:

```text
DerivationRuleRef[TSource, TSelection]
```

Then the builder accepts only compatible rules:

```python
User.derive(
    "UserPublic",
    lambda d: d.apply(PublicObjectFields),
)
```

A schema-field rule should not accidentally be applied to an event, operation or workflow.

Possible typed rule categories include:

```text
FieldSelectionRuleRef[T]
FieldModificationRuleRef[T]
SchemaDerivationRuleRef[TSource]
MappingRuleRef[TSource, TTarget]
```

Avoid a generic rules dictionary:

```python
rules["public"]
```

Prefer direct typed refs:

```python
PublicFields
MutableFields
CreateInputFields
```

---

## 11. Capabilities can be grouped into reusable profiles

Instead of repeating individual capability declarations:

```python
PublicReadableField = author.field_capability_profiles.define(
    "PublicReadableField",
    lambda c: c
        .exposure.public()
        .selectable()
)
```

Then:

```python
User.field_capabilities(
    lambda f: f
        .apply(f.id, PublicReadableField)
        .apply(f.display_name, PublicReadableField)
)
```

Or:

```python
User.field_capabilities(
    lambda f: f.fields(
        lambda fields: (
            fields.id,
            fields.display_name,
        ),
        PublicReadableField,
    )
)
```

Again, nothing is inferred. The author explicitly applies a reusable capability profile.

This gives you:

* Central capability policy
* Consistent field treatment
* Less repetition
* Explicit schema-level application
* Reusable derivation filtering

---

## 12. Capability names should not be arbitrary strings

Your examples conceptually refer to “capability X.” In the actual strongly typed API, that should normally be a reference or typed capability member.

Avoid:

```python
d.include_capability("public")
```

Prefer:

```python
d.include(lambda f: f.capabilities.has(PublicExposure))
```

Or:

```python
d.include(lambda f: f.capabilities.exposure.public)
```

For custom application-defined capabilities, declare them once:

```python
PublicApiField = author.capabilities.field.define(
    "publicApiField"
)
```

Then:

```python
User.field_capabilities(
    lambda f: f.assign(
        lambda fields: (
            fields.id,
            fields.display_name,
        ),
        PublicApiField,
    )
)
```

And:

```python
UserPublic = User.derive(
    "UserPublic",
    lambda d: d.include(
        lambda f: f.capabilities.has(PublicApiField)
    ),
)
```

The canonical IR can serialize the capability identity as text, but users pass typed refs.

---

## 13. Derivation provenance becomes much better

Every derived schema should record exactly how it was produced:

```text
Derived schema: UserPublic
Source schema: User
Operations:
  1. Applied rule PublicFields
  2. Explicitly included User.id
  3. Excluded User.internal_note
  4. Renamed User.display_name to name
```

For mapped shapes:

```text
Derived schema: CreateUserInput
Source schema: User
Operations:
  1. Removed first_name
  2. Removed last_name
  3. Added full_name
  4. Declared full_name → first_name + last_name mapping
```

This is valuable for:

* Diagnostics
* Documentation
* Change-impact analysis
* Template explanations
* Schema-diff reporting
* AI tooling without AI guesswork
* Reproducibility

---

## 14. Ordering and precedence must be deterministic

Because derivations may combine reusable rules and explicit changes, the plan needs a clear order.

A sensible order is:

```text
1. Start from source schema.
2. Apply reusable selection rules in declaration order.
3. Apply explicit includes and excludes.
4. Apply field usage modifications.
5. Apply renames and replacements.
6. Add new fields.
7. Register semantic mappings.
8. Validate resulting shape.
9. Freeze provenance.
```

But conflicts should not silently use “last write wins.”

For example:

```python
d.include(lambda f: f.email)
d.exclude(lambda f: f.email)
```

Dryv should either require an explicit override operation or report a conflict.

A deliberate override could look like:

```python
d.override.exclude(lambda f: f.email)
```

The exact syntax is open, but implicit ambiguity should be rejected.

---

## 15. Derived schemas should remain ordinary schemas

This principle should remain locked:

```text
Schema derivation
    ↓
ordinary immutable Schema
```

Templates and operations should not need separate APIs for:

* Base schemas
* Picked schemas
* Capability-filtered schemas
* Mapped schemas
* Extended schemas
* Partial schemas

All are schemas in the final contract.

Their provenance differs, but their semantic identity is the same kind:

```text
SchemaRef[T]
```

That avoids parallel schema hierarchies.

---

## 16. Revised conceptual model

Your improved design becomes:

```text
Structural schema
      │
      ├── field capabilities declared explicitly
      │
      ├── tags declared explicitly
      │
      └── field refs exposed through typed selectors
                  │
                  v
      explicit derivation builder
      ├── typed picks and omissions
      ├── capability filters
      ├── tag filters
      ├── reusable session rules
      ├── requiredness/nullability changes
      ├── additions and extensions
      ├── renames and replacements
      └── typed semantic mappings
                  │
                  v
         ordinary derived schema
         with deterministic provenance
```

This is substantially better than fixed automatic `create`, `read`, `update` and `query` derivations.

## The strongest principle

The final rule should be:

> Field capabilities describe explicit reusable facts. Derivation rules explicitly select and transform fields using those facts. Dryv never invents a derived schema or decides what a capability means without an authored derivation.

And the lambda selector remains a central ergonomic feature:

```python
User.pick(
    "UserRead",
    lambda f: (
        f.id,
        f.email,
        f.display_name,
    ),
)
```

That approach is clean, readable and compatible with the builder-flow philosophy proven in the earlier Codepot design.
