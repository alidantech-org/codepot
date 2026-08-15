You are correct. I narrowed the model too aggressively and dropped several already-planned concepts.

The uploaded authoring guide contains a much fuller structure.

# Restored root model

```text
Contract
├── Groups
├── Workflows
└── Presentations
```

A Group owns connected domain meaning:

```text
Group
├── Properties
├── Schemas
├── Operations
├── Policies
├── Failures
├── Events
├── Storage mappings
├── Value sources
└── Views
```

Cross-cutting information includes:

```text
Tags
Guidance
Documentation
Provenance
Typed references
```

This is the model we should return to.

---

# 1. Schema

A Schema is the structural foundation.

It can connect authoring for:

```text
Schema
├── Fields
├── Field capabilities
├── References to other schemas
├── Derived schemas
├── Schema mappings
├── Storage mappings
├── Operations using it
├── Events carrying it
├── Views presenting it
└── Value sources exposing its values
```

Important distinction from the old guide:

> The Schema can be the connected authoring hub without becoming an ORM entity or owning every related object inside canonical IR.

For example, authoring may access storage through the schema, but compiled meaning remains:

```text
Schema
+
StorageMapping
```

This allows one schema to have:

* SQL storage;
* document storage;
* no storage;
* several storage mappings;
* fields stored differently in different mappings.

The earlier discussion about fields belongs under this concept, but we should leave it there for now.

---

# 2. Operation

Operation is the neutral behavior concept.

The guide defines it as:

```text
Operation
├── Inputs
├── Outputs
├── Failures
├── Effects
└── Facets
```

It may additionally declare:

```text
listens to Event
handles Event
subscribes to Event
emits Event
runs before or after another Operation
triggers Workflow
is triggered by View
uses Policies
```

The Operation owns those relationships.

An Event does not author reverse lists. Runtime derives them for templates.

## Inputs and outputs

Operations must support:

```text
no input
one input
multiple inputs
named inputs

no output
one output
multiple outputs
named outputs
```

The clean model is an explicit absence of input/output:

```text
InputUse  = none | schema use
OutputUse = none | schema use
```

This avoids inventing fake empty schemas merely to represent `void`.

Templates can then render:

```text
void
None
()
Unit
nil
Promise<void>
Task
```

according to their target language.

## Facets

Facets describe how an operation participates in a particular interaction or execution mechanism.

The old guide retained typed facets such as:

```text
HTTP
Access
Events
Execution
Trigger
Scheduling
```

More facets may exist later, but they must be closed, typed contracts—not arbitrary metadata bags.

An HTTP facet may define:

```text
method
path
input bindings
output bindings
statuses
headers
cookies
media types
serialization
```

An event transport facet may define:

```text
transported event use
topic/channel binding
serialization
delivery-related facts
```

These are facets of an Operation or Event usage, not new controller, endpoint, consumer, or producer roots.

---

# 3. Event

Event remains one business concept:

```text
Event
├── Identity
├── Documentation
├── Payload schema use
├── Policies or relevant facts
├── Tags/guidance
└── Supported event facts
```

The Event registers that the business occurrence exists.

Other concepts declare how they use it:

```text
Operation emits Event
Operation listens to Event
Operation handles Event
Operation subscribes to Event
Operation hooks around Event processing
Workflow waits for Event
Workflow emits Event
View reacts to Event
Presentation exposes Event-driven behavior
```

Runtime can derive:

```text
event.emitters
event.listeners
event.handlers
event.subscribers
event.workflows
event.views
```

for selection, templating, tracing and auditing.

Those are derived relationships, not duplicated event authorship.

Events use the same Schema concept for payload typing. There is no separate `EventPayloadSchema` concept.

---

# 4. Workflow

Workflow is a compositional behavior concept.

```text
Workflow
├── Inputs
├── Outputs
├── Operations
├── Events
├── Policies
├── Failures
├── Steps
├── Transitions
├── Decisions
├── Branches
├── Waits
├── Compensation
├── Guidance
└── Tags
```

Its internal building blocks reuse existing concepts:

```text
Operation step
Event wait
Event emission
Schema-typed input/output
Policy condition
Failure path
Compensation operation
Child workflow
```

This avoids creating separate heavy roots for every workflow behavior.

A Workflow can express a simple sequence:

```text
Operation
→ Operation
→ Operation
```

or a more advanced process:

```text
Operation
→ Decision
    ├── Operation
    └── Wait for Event
→ Compensation on failure
```

Workflow steps and transitions may need typed references for authoring, but that does not automatically make them equal to Contract-level root concepts.

---

# 5. View

The old guide had **View** as a separate concept before Presentation.

A View is a neutral interaction unit owned by a Group:

```text
View
├── Schemas it uses
├── Fields it exposes
├── Parts
├── Value sources
├── Operations it triggers
├── Events it reacts to
├── Policies/access
├── Connections to other views
├── Guidance
└── Tags
```

A View is not automatically:

```text
page
screen
form
component
table
modal
CLI command
```

Those are emitted representations selected by packs.

Examples of semantic views might be:

```text
Browse pools
Edit pool
Booking details
Checkout review
Notification preferences
```

---

# 6. Presentation

Presentation composes complete application surfaces.

```text
Presentation
├── Identity
├── Channel
├── Views
├── View placements
├── Addresses
├── Navigation
├── Shell relationships
├── Access policies
├── Operations
├── Events
├── Workflows
├── Guidance
└── Tags
```

It can represent:

```text
organiser web application
customer web application
driver mobile application
provider mobile application
admin application
CLI application
desktop application
documentation portal
conversational application
```

Presentation does not define:

```text
React
Flutter
SwiftUI
Next.js
CSS
widget trees
component libraries
state-management libraries
```

Packs decide those representations.

The guide left one structural question unresolved:

```text
Does Contract directly own Presentations,
or are they placed under another explicit container?
```

The feature itself was retained; only exact ownership was undecided.

---

# 7. Policy

Policy is a reusable neutral rule or access requirement.

```text
Policy
├── Identity
├── Inputs/context
├── Composition
├── Documentation
├── Guidance
└── Tags
```

Policies may be used by:

```text
Operations
Views
Presentations
Workflows
Storage behavior where appropriate
```

The guide included:

```text
credentials
principals
roles
public access
protected access
policy composition
```

Policies prevent access logic from being repeatedly re-authored on HTTP routes, controllers, screens and workflow steps.

---

# 8. Failure

Failure was also preserved as typed meaning.

```text
Failure
├── Identity
├── Meaning
├── Payload schema use
├── Documentation
└── Relevant facet representations
```

Operations reference failures:

```text
Operation may fail with Failure
```

HTTP or another facet can then map a Failure to:

```text
status code
response schema
transport error code
```

The failure itself remains transport-neutral.

---

# 9. Storage mapping

Storage mapping is connected to Schema but remains explicit:

```text
StorageMapping
├── Schema
├── Store identity
├── Field mappings
├── Primary keys
├── Unique constraints
├── Indexes
├── Generated fields
├── Stored fields
├── Computed fields
├── Omitted fields
└── Relationships
```

The authoring experience may expose it through the Schema handle, but canonical meaning does not collapse Schema and persistence.

---

# 10. Value source

ValueSource connects existing concepts:

```text
ValueSource
├── Source Operation
├── Output collection/item
├── Value field
├── Label fields
├── Search input
└── Dependent inputs
```

It can support:

```text
web selector
mobile picker
CLI prompt
documentation
test generation
conversational choice
```

It does not define a dropdown or framework fetch function.

---

# 11. Property

The guide also had reusable Property definitions.

```text
Property
├── Type
├── Format
├── Constraints
├── Documentation
├── Tags
└── Provenance
```

Properties allow consistent reuse across schemas without copying primitive definitions and rules.

Examples include conceptual reusable values such as:

```text
Email
Money
Identifier
Slug
Timestamp
Phone number
```

---

# Restored concept relationship

```text
Contract
├── Groups
│   ├── Properties
│   ├── Schemas
│   │   ├── Fields
│   │   ├── Capabilities
│   │   ├── Derivations
│   │   └── Mappings
│   ├── Policies
│   ├── Failures
│   ├── Events
│   ├── Operations
│   │   ├── Inputs/outputs
│   │   ├── Failures
│   │   ├── Effects
│   │   └── Facets
│   ├── Storage mappings
│   ├── Value sources
│   └── Views
├── Workflows
└── Presentations
```

# Correct review order

We should now review the roots in this order:

```text
1. Contract and Group
2. Property
3. Schema
4. Policy
5. Failure
6. Event
7. Operation
8. StorageMapping
9. ValueSource
10. View
11. Workflow
12. Presentation
13. Tags, guidance and provenance
```

This restores the old authoring plan while incorporating the decisions made in the current discussion:

```text
[RESTORED] Full concept catalog from the old guide
[APPROVED] Event relationships are authored by the active concept
[APPROVED] Reverse event relationships may be derived for templates
[APPROVED] Field structure and field capabilities remain separate
[APPROVED] Language adapters are eliminated

[TO REVIEW] Explicit no-input/no-output operation representation
[TO REVIEW] Final facet catalog
[TO REVIEW] Workflow internal composition model
[TO REVIEW] Exact ownership of Presentations
[TO REVIEW] Which concepts are directly selectable
```

We should continue at the root level with **Contract and Group**, not return to fields yet.



Agreed. We should now **freeze the recovered direction as the working baseline** and refine it without silently replacing, removing, renaming, or expanding concepts.

## Working baseline

```text
Contract
├── Groups
│   ├── Properties
│   ├── Schemas
│   ├── Policies
│   ├── Failures
│   ├── Events
│   ├── Operations
│   ├── Storage mappings
│   ├── Value sources
│   └── Views
├── Workflows
└── Presentations
```

Status:

```text
[PARTIALLY APPROVED] Overall direction and concept family
[NOT YET APPROVED] Exact ownership hierarchy
[NOT YET APPROVED] Exact names
[NOT YET APPROVED] Exact responsibilities
[NOT YET APPROVED] Selectability and template variables
```

## Rules to prevent drift

### 1. Never silently change the catalog

Every concept change must be explicit:

```text
ADD
REMOVE
RENAME
MERGE
SPLIT
MOVE
KEEP
```

Example:

```text
[PROPOSED MOVE]
Presentation:
Contract → Presentation
instead of
Contract → Group → Presentation
```

Nothing becomes accepted until you approve it.

### 2. Separate four questions

For each root concept, we review only:

```text
1. Meaning
2. Authorability
3. Relationships
4. Runtime and template accessibility
```

We do not jump into Python syntax, generated files, or framework examples before the meaning is stable.

### 3. Keep authored and derived information separate

```text
Authored:
Operation emits Event

Derived:
Event.emitters
```

Derived reverse relationships may be exposed to templates but must not become duplicated authoring.

### 4. Reuse existing concepts before adding new ones

Before proposing a new concept, we must ask:

```text
Can this be expressed using:
Schema
Operation
Event
Workflow
Policy
Failure
View
Presentation
or another existing root?
```

A new root is added only when composition becomes unclear or loses essential meaning.

### 5. Do not confuse concepts with generated roles

These remain template outputs:

```text
DTO
entity
controller
service
repository
use case
handler class
subscriber class
page
screen
component
form
reducer
ViewModel
```

They do not automatically become canonical roots.

### 6. Keep a permanent decision ledger

Every discussion should end with:

```text
APPROVED
PARTIALLY APPROVED
PROPOSED
REJECTED
DEFERRED
UNREVIEWED
```

Rejected ideas stay recorded so they are not accidentally reintroduced later.

## Review format

For each concept:

```text
Concept: Operation

Meaning:
What it represents.

Owns:
Information authored directly on it.

References:
Other concepts it may use.

Derived relationships:
Information Runtime may calculate.

Used by templates:
Context exposed during generation.

Must not own:
Boundaries preventing overlap.

Open questions:
Anything still undecided.

Status:
UNREVIEWED | PROPOSED | PARTIALLY APPROVED | APPROVED
```

## Current locked decisions

```text
[APPROVED]
- Runtime IR is the semantic authority.
- Language adapters are eliminated.
- Templates own target-language syntax.
- Schema field definitions and field capabilities are separate.
- Relationship owners author forward relationships.
- Runtime may derive reverse relationships for templates and audit.
- Schema is reused wherever typed structure is needed.
- Advanced systems should compose existing concepts before adding roots.
```

```text
[PARTIALLY APPROVED]
- Contract, Group, Property, Schema, Policy, Failure,
  Event, Operation, StorageMapping, ValueSource,
  View, Workflow and Presentation form the working concept family.
```

```text
[REJECTED]
- Separate schema concepts for event payloads, notification data,
  workflow input and similar contexts.
- Events owning authored emitter/listener/subscriber lists.
- Creating canonical roots directly from infrastructure records.
- Previously proposed weak Python authoring examples.
```

We should now refine the root model **one concept at a time**, starting with `Contract` and `Group`, while preserving this ledger throughout.



## Core conclusion

**The research does not require many new root concepts.**

The existing root family is broad enough:

```text
Contract
├── Groups
│   ├── Properties
│   ├── Schemas
│   ├── Policies
│   ├── Failures
│   ├── Events
│   ├── Operations
│   ├── Storage mappings
│   ├── Value sources
│   └── Views
├── Workflows
└── Presentations
```

Most research findings should become:

1. typed capabilities inside these roots;
2. relationships between these roots;
3. reusable authoring compositions;
4. pack-generated representations.

My recommendation is:

> **Add no new top-level root concepts from the recent research yet.**

---

# 1. What must be added explicitly

These are not new roots. They are missing typed capabilities required inside the existing concepts.

## A. Operation input and output completeness

Operation must explicitly support:

```text
no input
one input
multiple inputs
named inputs

no output
one output
multiple outputs
named outputs
```

The no-input/no-output case must be semantic, not represented by fake empty schemas.

Templates can later render it as:

```text
void
Unit
None
()
nil
Task
Promise<void>
```

Operation inputs and outputs continue using the normal Schema concept whenever data exists.

---

## B. Operation participation in Events

The Operation authors the active relationship:

```text
Operation emits Event
Operation listens to Event
Operation handles Event
Operation subscribes to Event
```

Event remains a single business concept:

```text
Event
├── identity
├── meaning
└── optional payload using Schema
```

Runtime derives reverse information:

```text
Event emitters
Event listeners
Event handlers
Event subscribers
```

Templates may receive those derived lists.

### Hooks

Hooks should also be authored on the active side:

```text
Operation runs before Operation
Operation runs after Operation
Operation wraps Operation
```

Or through approved execution phases.

Hooks do not become a root concept.

---

## C. Typed Operation facets

The old guide already includes facets. Research shows they need to be completed rather than replaced.

```text
Operation
├── HTTP facet
├── Access facet
├── Trigger facet
├── Execution facet
├── Scheduling facet
└── Events/transport facet
```

### HTTP facet

May contain:

```text
method
path
input bindings
output bindings
status mappings
headers
cookies
media types
serialization
```

### Event transport facet

May contain typed facts such as:

```text
event relationship
payload binding
channel/topic binding
serialization
durability requirement
ordering requirement
retry behavior
idempotency behavior
concurrency behavior
```

These are facets of how an Operation uses an Event.

They are not authored on the Event as reverse relationships.

### Execution and scheduling facets

Can express:

```text
synchronous or asynchronous
scheduled execution
timer/cron trigger
timeout
retry behavior
execution hooks
```

The exact fact names remain to be reviewed.

---

## D. Workflow internal composition

Workflow remains one root, but its internal vocabulary must be explicit enough to compose the advanced patterns found in research.

```text
Workflow
├── input/output Schema uses
├── Operation steps
├── Event waits
├── Event emissions
├── Workflow references
├── decisions
├── branches
├── transitions
├── conditions
├── failure paths
└── compensation Operations
```

These are internal workflow elements, not top-level roots.

A simple workflow can remain:

```text
Operation
→ Operation
→ Operation
```

A complex workflow can compose:

```text
Operation
→ Decision
    ├── Operation
    └── Wait for Event
→ Compensation Operation on failure
```

We should not add every BPMN-style node immediately. We should add the smallest typed internal vocabulary that can expand without redesigning Workflow.

---

## E. Schema mapping and derivation

This was already in the old guide and should remain explicit.

Schema handles:

```text
fields
field capabilities
derivations
schema mappings
references
```

Schema mappings are needed for:

```text
rename
split
combine
flatten
nest
one-to-one
one-to-many
many-to-one
directionality
lossiness
reversibility
```

These are still relationships between ordinary Schema definitions.

No separate DTO, event-payload schema, notification schema, query schema, or frontend-state schema root is needed.

---

## F. View relationships

View should explicitly be able to:

```text
use Schema
use ValueSource
trigger Operation
trigger Workflow
react to Event
require Policy
contain nested View parts
connect to another View
```

This allows frontend behavior without introducing roots such as:

```text
Action
Reducer
ViewModel
Store
Form
Page
Screen
```

Those may be generated representations.

---

## G. Presentation composition

Presentation should explicitly compose application surfaces:

```text
Presentation
├── channel
├── placed Views
├── addresses
├── navigation
├── shell relationships
├── access Policies
├── entry points
└── guidance
```

A Presentation can use Views that connect to Operations, Events, Workflows and Schemas.

Presentation itself does not need to directly copy all those relationships.

The complete trace is already available:

```text
Presentation
→ View
→ Operation / Workflow / Event / Schema
```

---

## H. Runtime-derived template context

The Runtime should derive indexes and lists without changing authorship.

Examples:

```text
schema.operations_using_it
schema.views_using_it
schema.storage_mappings

event.emitters
event.listeners
event.workflows
event.views

operation.triggering_views
operation.related_events
operation.workflow_usages

view.presentations
workflow.triggering_operations
```

These are template and audit conveniences.

They are not duplicated authored properties.

---

# 2. What should be composed from existing concepts

## Command

A command is an Operation authoring convenience or typed operation fact:

```text
Operation
├── write-oriented intent
├── input Schema
├── output Schema or no output
└── possible Events
```

No `Command` root.

---

## Query

A query is also an Operation:

```text
Operation
├── read-oriented intent
├── input Schema or no input
└── output Schema
```

No `Query` root.

---

## Listener, handler, subscriber and emitter

These are Operation relationships with an Event:

```text
listener   = Operation listens to Event
handler    = Operation handles Event
subscriber = Operation subscribes to Event
emitter    = Operation emits Event
```

Templates may emit differently named classes or functions.

No listener, handler, subscriber or emitter roots.

---

## Scheduled job

Compose:

```text
Operation
+
Trigger/Scheduling facet
+
optional Workflow
```

The pack may emit a cron job, BullMQ processor, worker, Hangfire job or scheduled function.

No `Job` root.

---

## Notification system

Compose:

```text
Schemas
├── notification data
├── recipient data
└── delivery results

Events
├── notification requested
├── notification sent
└── notification failed

Operations
├── resolve recipients
├── render content
├── send
└── record result

Workflow
└── optional scheduling/retry process

Views
├── notification preferences
└── notification history

Presentation
└── web/mobile/admin placement
```

No `Notification` root is required.

A reusable authoring helper could create this composition, but it must compile into normal concepts.

---

## Transactional outbox

Compose:

```text
Operation emits Event
+
event/execution facet requests durable publication
+
StorageMapping or generated infrastructure
```

The pack may emit:

```text
outbox entity/table
publisher
recovery worker
queue integration
handler execution records
dead-letter processing
```

Those are generated implementation choices.

No `Outbox` root.

---

## Integration event

Use an ordinary Event.

Where internal and external contracts differ:

```text
Internal Event
→ mapping Operation
→ External Event
```

Their payloads use ordinary Schemas and Schema mappings.

Transport publication is defined through the emitting Operation’s event facet.

No `IntegrationEvent` root.

---

## Read model or projection

Compose:

```text
derived Schema
+
StorageMapping
+
Operation listening to Event
+
read/query Operations
+
optional Views
```

No `ReadModel` root.

---

## CQRS

Compose:

```text
read-oriented Operations
write-oriented Operations
Events
Schemas
StorageMappings
```

CQRS may be an authoring helper or pack convention.

No `CQRS` root.

---

## Saga or process manager

Compose:

```text
Workflow
+
Operations
+
Events
+
failure paths
+
compensation Operations
```

No `Saga` or `ProcessManager` root.

---

## State machine

Compose inside Workflow:

```text
states
transitions
conditions
Operations
Events
```

For a simple domain status field, it may instead be:

```text
Schema field
+
Operations changing it
+
Policies validating transitions
+
Events reporting changes
```

No separate state-machine root is required yet.

---

## Frontend feature architecture

The Swift, Android, React and Flutter patterns can be expressed as:

```text
Schema
└── feature/view state

View
├── uses state Schema
├── triggers Operations
├── reacts to Events
└── contains parts

Operation
└── user or system behavior

Presentation
└── places the View
```

Packs can emit:

```text
Reducer
ViewModel
Store
Action enum
Effect
React hook
Flutter controller
SwiftUI View
Android ViewModel
```

No reducer, action, effect or store roots.

---

## API resource

Compose:

```text
Schema
+
Operations
+
HTTP facets
+
Policies
+
Failures
+
StorageMapping
```

Packs may emit:

```text
controller
DTO
service
repository
use case
client
OpenAPI
```

No API-resource root is necessary.

---

# 3. What should remain template or runtime implementation only

These should not enter the semantic root catalog:

```text
DTO
entity
ORM model
controller
resolver
service class
repository class
use-case class
handler class
subscriber class
producer class
queue worker
outbox row
handler execution record
delivery attempt
workflow run
workflow checkpoint
queue job
broker message
provider response
page
screen
component
form
table
reducer
ViewModel
store
SDK method
```

Dryv can generate these, trace them and expose their planned artifacts.

But they are not authored business concepts.

---

# 4. Clean three-level classification

## Level 1: Root concepts

Keep the current family:

```text
Property
Schema
Policy
Failure
Event
Operation
StorageMapping
ValueSource
View
Workflow
Presentation
```

No additions recommended from the research yet.

## Level 2: Typed internal capabilities

Explicitly add or complete:

```text
Operation input/output absence
Operation Event relationships
Operation hooks
Operation facets
Schema capabilities
Schema derivations and mappings
Workflow internal composition
View triggers and reactions
Presentation placements and navigation
Runtime-derived reverse relationships
```

These need canonical typed contracts.

## Level 3: Composition patterns

Provide reusable authoring helpers for:

```text
CRUD
API resources
CQRS
event-driven processing
outbox delivery
notifications
read models
sagas
state machines
scheduled jobs
frontend features
admin applications
mobile applications
```

These helpers must compile into Level 1 and Level 2 constructs.

They must not add private semantic objects.

---

# Rule for future additions

A research concept becomes a new root only when all of these are true:

1. It has independent, language-neutral meaning.
2. It cannot be represented clearly by composing existing roots.
3. Several other roots need to reference it directly.
4. It needs independent identity, documentation and provenance.
5. Templates need to select it independently.
6. It remains stable across different languages and frameworks.

Most newly researched nouns fail this test because they are:

* operation roles;
* workflow internals;
* infrastructure implementations;
* generated file roles;
* reusable compositions.

---

# Recommended decision ledger

```text
[KEEP — PARTIALLY APPROVED ROOT FAMILY]
Property
Schema
Policy
Failure
Event
Operation
StorageMapping
ValueSource
View
Workflow
Presentation
```

```text
[PROPOSED EXPLICIT ADDITIONS INSIDE EXISTING ROOTS]
- no-input and no-output Operation uses
- Operation-authored Event relationships
- typed Operation hooks
- completed HTTP/access/trigger/execution/scheduling/event facets
- Schema mappings and capability-based derivation
- Workflow operations, event waits, decisions, branches and compensation
- View operation/workflow triggers and Event reactions
- Presentation placements, addresses and navigation
- Runtime-derived reverse relationship contexts
```

```text
[PROPOSED COMPOSITION PATTERNS — NOT ROOTS]
- command
- query
- listener
- subscriber
- notification system
- outbox
- integration event flow
- read model
- CQRS
- saga/process manager
- state machine
- scheduled job
- frontend feature
- API resource
```

This keeps Dryv small without making it weak:

> **The root vocabulary stays stable. Typed relationships make it expressive. Composition creates advanced systems. Packs turn those systems into concrete code.**

# Research conclusion

Clean Architecture, Hexagonal Architecture, Onion Architecture, DDD, Vertical Slice Architecture, SOLID, and modular-monolith practices do **not** require a larger Dryv root vocabulary.

They reveal two things Dryv must support:

1. richer semantic boundaries inside the existing concepts;
2. architecture rules inside template packs and generation planning.

The existing roots remain:

```text
Contract
├── Groups
│   ├── Properties
│   ├── Schemas
│   ├── Policies
│   ├── Failures
│   ├── Events
│   ├── Operations
│   ├── StorageMappings
│   ├── ValueSources
│   └── Views
├── Workflows
└── Presentations
```

Do **not** add roots named:

```text
Entity
ValueObject
Aggregate
UseCase
Service
Repository
Port
Adapter
Controller
Presenter
Layer
VerticalSlice
CleanArchitecture
```

Those are either roles, traits, relationships, compositions, or generated representations.

---

# 1. The architectural principles worth preserving

## Dependency direction

Clean Architecture’s central rule is that source dependencies point toward higher-level business policy. Frameworks, databases, web transports, and UI mechanisms remain outside the core. Data crossing a boundary should use structures suitable for the inner policy rather than ORM rows or framework-specific request objects. Robert Martin also states that the familiar four circles are illustrative rather than mandatory. ([Clean Coder Blog][1])

For Dryv this means:

```text
Runtime IR expresses business meaning.
Packs generate boundaries and dependency direction.
Framework types must not leak into core generated artifacts.
```

## Ports and adapters

Hexagonal Architecture makes the application usable independently of a particular UI or database. External technology enters through adapters connected to application ports. ([Alistair Cockburn][2])

For Dryv:

```text
Operation = semantic callable contract
Facet/binding = interaction mechanism
Generated adapter = implementation representation
```

A port does not need to become a new root.

## Architecture should reveal the business

Screaming Architecture argues that the top-level system structure should reveal use cases such as inventory, accounting, or healthcare—not Rails, Spring, databases, or web delivery. ([Clean Coder Blog][3])

For Dryv, output paths should usually be driven by:

```text
Group
Operation
Workflow
Presentation
```

rather than only:

```text
controllers/
services/
repositories/
dtos/
```

## DDD boundaries and tactical patterns

DDD distinguishes bounded contexts, identity-bearing entities, value objects, aggregate consistency boundaries, domain services, application services, repositories, and domain events. It also recommends domain events for coordination across aggregate boundaries. ([Microsoft Learn][4])

However, Microsoft’s guidance also says simple CRUD domains may not benefit from rich DDD patterns. Different bounded contexts may legitimately use different architectural complexity. ([Microsoft Learn][4])

Therefore Dryv must support rich architecture without forcing it everywhere.

## Vertical slices

Vertical Slice Architecture organizes code around requests or use cases rather than forcing every feature through the same horizontal service/repository layering. ([Jimmy Bogard][5])

This should be a pack layout option, not a different Runtime IR.

---

# 2. What must be added explicitly to existing concepts

## A. Strengthen `Group` as a boundary

`Group` should become the neutral equivalent of a domain module or bounded context.

It needs to express:

```text
Group
├── owns concepts
├── exposes concepts
├── keeps concepts internal
├── depends on other Groups
└── limits which external surfaces it may use
```

### Required capabilities

```text
public surface
internal surface
allowed Group dependencies
cross-Group references
provided Operations and Events
required Operations and Events
```

This enables Dryv to validate:

```text
No illegal access to internal concepts.
No dependency on an unapproved Group.
No accidental cyclic Group dependencies.
No cross-Group reference that bypasses the public surface.
```

Spring Modulith validates the same broad architectural properties in generated Java systems: no module cycles, access through exposed APIs only, and optional explicit allowed dependencies. ([Home][6])

### Important boundary

A `Group` is semantic.

A generated representation might be:

```text
package
namespace
crate
module
assembly
project
folder
service
microservice
```

The pack chooses that representation.

---

## B. Add domain characteristics to `Schema`

Entity, value object, and aggregate should not become roots. They should be expressible through typed Schema characteristics.

### Identity semantics

A Schema may declare:

```text
no identity
one identity field
composite identity
generated identity
externally supplied identity
```

A Schema with identity semantics can be emitted as an entity where appropriate.

### Value semantics

A Schema may declare:

```text
value equality
identity equality
immutability
replace-as-a-whole behavior
```

A value-semantic Schema may become a C# record, Kotlin data class, Rust value type, TypeScript readonly type, Swift struct, or another pack-selected representation.

### Aggregate composition

Schemas need typed relationships capable of expressing:

```text
aggregate root
aggregate member
ownership
consistency boundary
external aggregate reference by identity
```

An aggregate root is responsible for protecting the consistency of its aggregate, while references across aggregates are commonly identity-based rather than direct object navigation. ([Microsoft Learn][4])

This remains Schema composition—not an `Aggregate` root.

### Invariants

Schema-related business invariants should reuse `Policy`:

```text
Schema
← governed by Policy
```

The pack may place the generated behavior inside an entity, aggregate root, validation function, constructor, factory, or service.

---

## C. Strengthen relationships between `Operation`s

Clean and Hexagonal architectures require a way to describe required behavior without coupling business policy to its concrete infrastructure implementation.

Add relationships such as:

```text
Operation invokes Operation
Operation requires Operation
Operation delegates to Operation
Operation composes Operations
```

Example:

```text
Checkout
├── requires ReserveInventory
├── requires CreatePaymentIntent
└── emits CheckoutStarted
```

The semantic operation does not know whether `CreatePaymentIntent` is implemented through:

```text
Stripe
PayPal
M-Pesa
a mock
an in-memory test adapter
```

A pack or project binding selects the provider and emits the appropriate interface and adapter.

This is the Dryv form of dependency inversion.

## Operation boundary data

Operation inputs and outputs must always use ordinary Schemas or explicit absence:

```text
input: Schema | none
output: Schema | none
```

An Operation should not receive:

```text
TypeORM entity
EF database row
Laravel request
NestJS request object
SwiftUI binding
framework response
```

Those belong to generated adapters.

---

## D. Complete Operation execution facts

Clean-code generation needs several operation-level facts:

```text
transaction boundary
consistency requirement
synchronous/asynchronous execution
retry policy
timeout
idempotency
concurrency requirement
side effects
```

These belong inside typed Operation facets or execution configuration.

They should not become roots such as:

```text
UnitOfWork
Transaction
Job
Retry
```

For example:

```text
Operation
+
transaction execution fact
+
StorageMapping
```

can generate a Unit of Work or framework transaction wrapper.

---

## E. Keep storage outside business structure

`StorageMapping` already provides the required separation:

```text
Schema
    semantic structure

StorageMapping
    persistence representation
```

This supports Clean Architecture’s requirement that the domain model not depend directly on an ORM or database. Microsoft’s DDD guidance similarly places repository implementations outside the domain model while allowing repository contracts to be expressed toward the domain side. ([Microsoft Learn][7])

A repository can be generated from:

```text
Schema identity and aggregate facts
+
StorageMapping
+
Operations requiring persistence
```

No `Repository` root is needed.

---

## F. Preserve mapping across boundaries

Clean Architecture warns against passing external framework formats directly into inner business policy. ([Clean Coder Blog][1])

Dryv already has the correct building blocks:

```text
External Schema
→ SchemaMapping
→ Internal Schema
```

This supports:

```text
HTTP request → operation input
database row → domain structure
external payment payload → internal payment result
domain event → public integration event
domain result → presentation view data
```

An anti-corruption layer becomes:

```text
Schemas
+
SchemaMappings
+
Operations
+
facets
```

No anti-corruption-layer root.

---

# 3. What belongs to template packs

## Architecture zones

A pack should be able to declare architectural zones:

```text
domain
application
ports
adapters
infrastructure
delivery
presentation
composition
```

These names must be pack-defined, not hardcoded into Runtime IR. Clean Architecture explicitly allows more or fewer circles as long as dependency direction remains correct. ([Clean Coder Blog][1])

A pack declares:

```text
artifact roles assigned to zones
allowed dependency directions
public and internal symbols
boundary-crossing rules
path conventions
composition roots
```

Example:

```text
domain may depend on nothing external
application may depend on domain
adapters may depend on application
infrastructure may implement application requirements
composition may depend on all required concrete artifacts
```

## Architecture profiles

A pack can provide different profiles:

```text
simple CRUD
clean layered
hexagonal
vertical slice
feature-sliced clean
modular monolith
DDD-rich
event-driven
```

These profiles use the same Runtime IR.

A project could even use different profiles per Group:

```text
catalog      → simple CRUD
ordering     → DDD-rich clean architecture
reporting    → CQRS read model
notifications → event-driven workflow
```

That matches the practical recommendation to apply richer DDD only where domain complexity justifies it. ([Microsoft Learn][4])

## Path strategy

A screaming/feature-first pack may generate:

```text
ordering/
  place-order/
  cancel-order/
  fulfill-order/
```

A layered clean pack may generate:

```text
ordering/
  domain/
  application/
  adapters/
  infrastructure/
```

A combined profile may generate:

```text
ordering/
  place-order/
    application/
    adapters/
  cancel-order/
    application/
    adapters/
  domain/
```

No semantic changes are required.

---

# 4. Mapping accepted architecture ideas to Dryv

| Architecture idea         | Dryv representation                            | Possible generated role                  |
| ------------------------- | ---------------------------------------------- | ---------------------------------------- |
| Bounded context/module    | `Group`                                        | package, namespace, crate, project       |
| Entity                    | identity-bearing `Schema`                      | entity class, domain struct              |
| Value object              | value-semantic `Schema`                        | record, immutable class, struct          |
| Aggregate root            | Schema aggregate characteristic                | aggregate root class                     |
| Aggregate member          | Schema ownership relationship                  | child entity/value object                |
| Use case                  | `Operation`                                    | handler, interactor, application service |
| Domain service            | Operation using domain Schemas and Policies    | domain service/function                  |
| Application service       | Operation composing other Operations           | orchestrator/interactor                  |
| Specification             | `Policy`                                       | predicate/specification class            |
| Domain event              | `Event`                                        | event record/class                       |
| Port                      | referenced or required `Operation` contract    | interface/protocol/trait                 |
| Adapter                   | facet/project binding                          | controller, gateway, consumer            |
| Repository contract       | persistence Operations around aggregate Schema | interface/trait                          |
| Repository implementation | `StorageMapping` plus pack binding             | ORM repository                           |
| Unit of Work              | Operation execution facts                      | transaction wrapper                      |
| DTO                       | Operation-boundary Schema representation       | DTO/request/response type                |
| Controller                | HTTP facet on Operation                        | controller/route handler                 |
| Presenter                 | `View`/Presentation mapping                    | presenter/view model mapper              |
| Factory                   | creation Operation plus Schema rules           | factory/constructor                      |
| Anti-corruption layer     | SchemaMapping plus Operations                  | adapter/translator                       |
| CQRS                      | read/write Operations and Schemas              | command/query handlers                   |
| Saga/process manager      | Workflow using Operations and Events           | saga/workflow executor                   |
| Composition root          | pack planning artifact                         | DI bootstrap/main module                 |

---

# 5. SOLID as generation rules

SOLID should not add concepts. It should constrain generated artifacts.

## Single Responsibility

A generated artifact should have one clear reason to change.

Avoid automatically producing a single giant service containing:

```text
queries
commands
validation
mapping
storage
event publication
transport logic
```

The pack should be able to emit smaller operation-oriented artifacts.

## Open/Closed

New adapters, presentations, storage providers, or transports should be addable without modifying core business artifacts. Robert Martin connects this principle to plugin-style architectures where low-level plugins depend on stable core contracts. ([Clean Coder Blog][8])

Dryv pack composition directly supports this:

```text
stable Runtime IR
+
additional pack
+
new binding
```

## Interface Segregation

Do not always generate one enormous service interface containing every Operation in a Group.

Allow pack policies such as:

```text
one port per Operation
one port per capability
one port per feature
one port per cohesive Operation set
```

## Dependency Inversion

Core artifacts depend on operation contracts and semantic schemas. Concrete adapters depend on those contracts—not the reverse. This is the central Clean Architecture dependency rule and remains relevant across statically typed languages such as Java, C#, Go, and Swift. ([Clean Coder Blog][9])

## Substitution and conformance

Every generated adapter claiming to implement an Operation must satisfy:

```text
input contract
output contract
failure contract
execution expectations
```

Dryv can generate contract tests to verify this.

---

# 6. Architecture validation Dryv should provide

Because Dryv plans every artifact, symbol, import, and dependency before rendering, it can validate architecture more reliably than a normal text generator.

## Semantic validation

```text
Group references an internal concept from another Group.
Group depends on a forbidden Group.
Schema aggregate member has no valid root.
Operation requires an unresolved Operation.
Operation uses a storage-specific Schema at a clean boundary.
Cross-boundary Schema mapping is missing.
```

## Planned-artifact validation

```text
Dependency points from core toward infrastructure.
Framework symbol leaks into a domain artifact.
Generated module dependency cycle exists.
Artifact imports an internal symbol across module boundaries.
Adapter has no corresponding operation contract.
Required operation has no bound provider.
Two conflicting adapters provide the same required operation.
```

## Generated architecture tests

Packs should be able to generate tests enforcing:

```text
dependency direction
forbidden imports
module cycles
public/internal boundaries
adapter conformance
operation contract conformance
architecture zone placement
```

Spring Modulith demonstrates the value of executable checks for cycles, internal access, and allowed module dependencies. ([Home][6])

---

# 7. What is explicitly new versus composed

## Proposed explicit additions

```text
[PROPOSED — GROUP]
- public versus internal concepts
- allowed Group dependencies
- provided and required surfaces
- derivable Group dependency graph

[PROPOSED — SCHEMA]
- identity semantics
- value semantics
- immutability characteristics
- aggregate-root and aggregate-member relationships
- invariant Policy references

[PROPOSED — OPERATION]
- invokes/requires/delegates relationships
- explicit no-input/no-output
- transaction and consistency facts
- provider binding support
- operation contract conformance

[PROPOSED — PACK MODEL]
- architecture zones
- allowed artifact dependency directions
- public/internal symbol policies
- architecture profiles
- composition-root artifacts
- generated architecture tests
```

## Composable with existing concepts

```text
Entity
Value object
Aggregate
Use case
Domain service
Application service
Port
Adapter
Repository
Factory
Unit of Work
Specification
Command
Query
CQRS
Saga
Process manager
Anti-corruption layer
Controller
Presenter
DTO
Vertical slice
```

## Still template outputs

```text
entity class
repository interface
repository implementation
controller
route
use-case class
service class
handler
gateway
presenter
view model
DTO
module
namespace
folder
project
architecture test
DI registration
```

# Recommended boundary

The cleanest design is:

> **Runtime IR describes business boundaries, structural semantics, operations, dependencies, policies, and relationships. Packs describe architectural zones, artifact roles, dependency direction, concrete ports/adapters, and filesystem layout.**

This gives Dryv accepted Clean Architecture and DDD capabilities without converting their implementation vocabulary into an oversized canonical model.

The next concept requiring careful refinement is `Group`, because it must support domain ownership, public surfaces, internal concepts, and allowed dependencies without becoming tied to packages, services, or any one architectural style.

[1]: https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html "https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html"
[2]: https://alistair.cockburn.us/hexagonal-architecture "https://alistair.cockburn.us/hexagonal-architecture"
[3]: https://blog.cleancoder.com/uncle-bob/2011/09/30/Screaming-Architecture.html "https://blog.cleancoder.com/uncle-bob/2011/09/30/Screaming-Architecture.html"
[4]: https://learn.microsoft.com/en-us/dotnet/architecture/microservices/microservice-ddd-cqrs-patterns/microservice-domain-model "https://learn.microsoft.com/en-us/dotnet/architecture/microservices/microservice-ddd-cqrs-patterns/microservice-domain-model"
[5]: https://www.jimmybogard.com/vertical-slice-architecture/ "https://www.jimmybogard.com/vertical-slice-architecture/"
[6]: https://docs.spring.io/spring-modulith/reference/verification.html "https://docs.spring.io/spring-modulith/reference/verification.html"
[7]: https://learn.microsoft.com/en-us/dotnet/architecture/microservices/microservice-ddd-cqrs-patterns/net-core-microservice-domain-model "https://learn.microsoft.com/en-us/dotnet/architecture/microservices/microservice-ddd-cqrs-patterns/net-core-microservice-domain-model"
[8]: https://blog.cleancoder.com/uncle-bob/2014/05/12/TheOpenClosedPrinciple.html "https://blog.cleancoder.com/uncle-bob/2014/05/12/TheOpenClosedPrinciple.html"
[9]: https://blog.cleancoder.com/uncle-bob/2020/10/18/Solid-Relevance.html "https://blog.cleancoder.com/uncle-bob/2020/10/18/Solid-Relevance.html"

Yes—both are important, but they need clean boundaries.

# 1. Schema inheritance

Dryv should support schema inheritance, but treat it as **schema derivation**, not programming-language class inheritance.

```text
BaseSchema
    ↓ extends
DerivedSchema
```

Example meaning:

```text
BaseRecord
├── id
├── createdAt
└── updatedAt

Pool extends BaseRecord
├── title
├── capacity
└── status
```

The resulting `Pool` schema contains the inherited and declared fields.

## What may be inherited

Inheritance can include:

```text
fields
field capabilities
validation rules
formats
documentation
policies attached to the schema
schema-level characteristics
```

But inheritance rules must be explicit for every category.

For example:

```text
Pool extends BaseRecord

Fields:
    inherited

Field capabilities:
    inherited, unless explicitly changed

Storage mappings:
    not inherited automatically

Operations:
    not inherited automatically
```

## Why storage mappings should not automatically inherit

A semantic inheritance relationship does not imply a database inheritance strategy.

```text
Pool extends BaseRecord
```

must not automatically mean:

```text
SQL table inheritance
single-table inheritance
joined-table inheritance
ORM entity inheritance
```

Those are storage or pack decisions.

A derived Schema may reuse or extend a StorageMapping explicitly, but the two relationships remain separate:

```text
Schema extends Schema
StorageMapping extends/reuses StorageMapping
```

## Override rules

Dryv needs deterministic rules:

```text
A derived schema cannot silently redefine a field incompatibly.

A field override must explicitly declare what changes.

Removing an inherited field must be explicit.

Conflicting inherited fields must fail validation.

Inheritance cycles are forbidden.
```

It should also support multiple structural reuse patterns without pretending they are all inheritance:

```text
extends
includes/composes
derives from
projects from
```

These have different meanings.

### `extends`

Represents a semantic specialization:

```text
Employee extends Person
```

### `includes` or composition

Reuses a structural part:

```text
Address included in Customer
```

### `derives`

Creates another schema representation:

```text
PoolSummary derived from Pool
```

These should not be collapsed into one vague mechanism.

---

# 2. ORM-added and SQL-added fields

We need to distinguish three cases.

## A. Semantically real fields

Fields such as:

```text
id
createdAt
updatedAt
version
tenantId
```

belong in the Schema when they are visible to business operations, APIs, events, workflows, or presentations.

A reusable base Schema can provide them:

```text
BaseRecord
├── id
├── createdAt
├── updatedAt
└── version
```

Then another Schema extends it.

## B. Persistence-only fields

Some fields exist only for storage implementation:

```text
internal row identifier
database partition key
ORM discriminator
materialized search vector
migration compatibility column
database checksum
```

These should not be forced into the semantic Schema.

They belong to the `StorageMapping`:

```text
StorageMapping
├── semantic field mappings
├── storage-only fields
├── generated columns
├── computed columns
└── omitted semantic fields
```

## C. Derived or generated semantic fields

A field may be semantically visible but generated by storage:

```text
createdAt
updatedAt
sequenceNumber
database-generated id
```

It remains a Schema field, while its generation mechanism belongs to StorageMapping:

```text
Schema field:
    createdAt

Storage mapping:
    generated by database
    column type = timestamptz
    default expression = current timestamp
```

The Schema defines **what the field means**.

The StorageMapping defines **how it is stored and produced**.

---

# 3. SQL checks and constraints

Checks need the same semantic-versus-storage distinction.

## Business invariant

Example:

```text
capacity must be non-negative
validUntil must be after validFrom
```

If this rule matters regardless of database technology, it should be expressed as a `Policy`, validation rule, or schema invariant.

```text
Schema
└── governed by Policy
```

That rule can be used by:

```text
operation validation
workflow decisions
generated application code
frontend validation
documentation
tests
SQL CHECK generation
```

## Storage-only constraint

Example:

```text
PostgreSQL-specific exclusion constraint
partial index predicate
database collation rule
storage engine check
```

This belongs only to `StorageMapping`.

## Constraint classification

```text
Business rule
    → Policy or schema validation
    → may be emitted as SQL CHECK

Persistence rule
    → StorageMapping only
```

Important: generating a SQL check from a business Policy is optional pack behavior. The SQL representation must not become the authority for the business rule.

---

# 4. What StorageMapping should support

The existing StorageMapping concept should explicitly cover:

```text
table or collection mapping
field-to-column mapping
storage-only fields
generated fields
computed fields
column types
nullability representation
defaults
primary keys
foreign keys
unique constraints
check constraints
indexes
partial indexes
relationship mappings
cascade behavior
concurrency/version columns
discriminators
inheritance strategy
serialization into columns
embedded structures
```

These are not Schema capabilities.

They describe persistence representation.

---

# 5. Can a Schema have Operations?

**In authoring: yes.**

**In canonical ownership: Operations should remain independent concepts.**

A schema-oriented authoring API should be able to express:

```text
Pool operation create
Pool operation update
Pool operation pause
Pool operation list
Pool operation findById
```

That is clean and easy to discover.

But after compilation, the meaning should remain:

```text
Group owns Operation
Operation is associated with Pool Schema
```

not:

```text
Schema permanently owns all Operation semantics
```

## Why Operations must remain independent

An Operation may:

### Use several Schemas

```text
TransferFunds
├── Account
├── Money
├── TransferRequest
└── TransferReceipt
```

### Have no primary Schema

```text
HealthCheck
SendDailyReport
RebuildSearchIndex
```

### Coordinate several domain concepts

```text
Checkout
├── Cart
├── Order
├── Payment
├── Inventory
└── Customer
```

### Exist primarily for an Event or Workflow

```text
HandlePaymentSucceeded
ExpireReservation
CompensateFailedOrder
```

Therefore, Schema cannot be the universal canonical owner of Operations.

---

# 6. The clean relationship

Operations can have an explicit semantic association with Schemas:

```text
Operation
├── subject Schemas
├── input Schema or none
├── output Schema or none
├── required Operations
├── emitted Events
└── other facets
```

For a normal CRUD-style operation:

```text
CreatePool
├── subject: Pool
├── input: CreatePoolInput
└── output: Pool
```

For a multi-schema operation:

```text
Checkout
├── subjects:
│   ├── Cart
│   ├── Order
│   └── Payment
├── input: CheckoutInput
└── output: CheckoutResult
```

Runtime can derive:

```text
Pool.operations
Pool.create_operations
Pool.query_operations
Pool.event_handlers
```

Templates may receive these lists.

They are derived from Operation-authored relationships.

---

# 7. Authoring convenience versus Runtime IR

The authoring experience can be schema-centered:

```text
Pool
├── define fields
├── define capabilities
├── configure storage
└── register related operations
```

But compilation normalizes it into independent canonical concepts:

```text
Schema: Pool

StorageMapping:
    schema = Pool

Operations:
    CreatePool.subjects = [Pool]
    UpdatePool.subjects = [Pool]
    PausePool.subjects = [Pool]
```

This follows the same principle already approved for Events:

```text
Convenient connected authoring
does not require duplicated canonical ownership.
```

---

# Recommended decisions

```text
[PROPOSED]
Schema inheritance is supported as explicit schema derivation.

[PROPOSED]
Schema inheritance and storage inheritance remain separate.

[PROPOSED]
Base schemas may provide reusable semantic fields,
capabilities, rules and documentation.

[PROPOSED]
Storage-only fields remain in StorageMapping.

[PROPOSED]
Business checks belong to Policy/schema validation and
may be emitted as database checks.

[PROPOSED]
Database-specific checks, indexes and constraints belong
to StorageMapping.

[PROPOSED]
Authoring may register Operations through a Schema handle.

[PROPOSED]
Canonical Operations remain independently owned by Group.

[PROPOSED]
Operation explicitly associates itself with one or more
subject Schemas.

[PROPOSED]
Runtime derives Schema-related Operation lists for templates.
```

The clean rule is:

> **Schemas may provide a convenient authoring surface for related operations, but Operations remain independent semantic concepts. Schema inheritance defines structural meaning; StorageMapping defines persistence inheritance and database behavior.**

Yes—**approved**.

## Approved schema extension model

A Schema may derive from another Schema and add fields:

```text
UserResponse
extends BaseResponse
adds:
    user: UserSchema
```

Meaning:

```text
BaseResponse
├── success
├── message
└── metadata

UserResponse
├── success       inherited
├── message       inherited
├── metadata      inherited
└── user          added, typed by UserSchema
```

Both of these ideas are supported:

```text
Schema extends BaseSchema
```

and:

```text
BaseSchema extended with additional fields
```

They describe the same canonical relationship from different authoring directions.

## Canonical meaning

```text
SchemaDerivation
├── base: BaseResponse
├── additions
│   └── user: reference to UserSchema
├── explicit overrides
└── resulting schema: UserResponse
```

`UserResponse` is still a normal Schema with its own identity. It can be used by:

```text
Operation output
Event payload
Workflow input/output
View data
another Schema field
```

## Important rules

### The base Schema is not mutated

Extending `BaseResponse` creates `UserResponse`; it does not add `user` to every response.

### Fields may reference other Schemas

```text
user: UserSchema
users: list of UserSchema
data: SomeOtherSchema
```

This supports nested responses and compositions cleanly.

### Inherited information retains provenance

Templates and inspection can determine:

```text
success came from BaseResponse
user was declared by UserResponse
```

### Overrides must be explicit

A derived Schema may deliberately change an inherited field only through an explicit override. Silent incompatible replacement is invalid.

### Extension does not imply storage inheritance

```text
UserResponse extends BaseResponse
```

does not imply ORM inheritance, SQL table inheritance, or shared persistence.

### Operations are not inherited automatically

Extending a Schema does not automatically copy operations associated with the base Schema. Any operation relationship must be explicit.

## Approved distinction

```text
extends
    creates a semantic derived Schema

adds / extendWith
    adds fields or other approved schema information
    while creating that derived Schema

reference field
    uses another Schema as a field type
```

## Decision ledger

```text
[APPROVED]
- Schemas may extend another Schema.
- A derived Schema may add fields.
- Added fields may reference other Schemas.
- Base Schemas remain unchanged.
- Derived Schemas retain their own identity.
- Inherited field provenance is preserved.
- Overrides must be explicit.
- Schema extension does not imply storage inheritance.
- Schema extension does not automatically inherit Operations.
```

Your example is therefore valid canonical meaning:

```text
UserResponse
    extends BaseResponse
    adds user: UserSchema
```


Yes. That is exactly the kind of relationship the **template pack** should be allowed to create.

The canonical Runtime IR only needs:

```text
Schema: User
```

The pack may select two templates for that Schema:

```text
Schema User
├── type template
└── entity template
```

The type template emits:

```ts
export interface User {
  id: string;
  name: string;
}
```

The entity template emits:

```ts
export class UserEntity implements User {
  id: string;
  name: string;
}
```

## How Dryv should model this

The type template provides a generated symbol:

```text
Artifact
├── role: type
├── subject: Schema(User)
└── provides symbol:
    ├── purpose: schema-type
    └── name: User
```

The entity template requires that symbol:

```text
Artifact
├── role: entity
├── subject: Schema(User)
└── requires symbol:
    ├── purpose: schema-type
    └── subject: Schema(User)
```

Dryv resolves:

```text
UserEntity template
→ requires User schema-type
→ finds User type artifact
→ creates artifact dependency
→ supplies import path and symbol name
```

The template then renders the target-language syntax:

```text
implements {{ schema_type.symbol }}
```

## Important distinction

This:

```ts
class UserEntity implements User
```

is a **generated TypeScript relationship**.

It does not mean the canonical Runtime IR contains:

```text
StorageMapping implements Schema
```

The Runtime IR relationship remains:

```text
StorageMapping maps Schema
```

The pack decides that its TypeScript representation will be:

```text
Schema
→ interface

StorageMapping
→ entity class implementing the interface
```

Another pack could generate:

### C#

```csharp
public interface IUser
{
    Guid Id { get; }
    string Name { get; }
}

public class UserEntity : IUser
{
    public Guid Id { get; set; }
    public string Name { get; set; }
}
```

### Java

```java
public interface User {
    UUID getId();
    String getName();
}

@Entity
public class UserEntity implements User {
    // ...
}
```

### A different TypeScript pack

```ts
export type User = {
  id: string;
  name: string;
};

export class UserEntity {
  id: string;
  name: string;
}
```

That pack may choose not to use `implements` because TypeScript classes cannot directly implement every possible type shape cleanly.

## Pack-level declaration

Conceptually, the pack needs to express:

```text
Template: schema-type
selects: Schema
provides:
    symbol(schema-type, subject=selected Schema)

Template: schema-entity
selects:
    StorageMapping whose mapped subject is selected Schema
requires:
    symbol(schema-type, subject=mapped Schema)
```

The entity template receives something like:

```text
schema
storageMapping
schemaTypeSymbol
schemaTypeImport
fields
mappedFields
```

Then it renders:

```ts
export class {{ entityName }}
  implements {{ schemaTypeSymbol }}
{
  ...
}
```

## This also supports multiple representations

One Schema may produce:

```text
User
├── User type
├── UserEntity
├── UserDto
├── UserResponse
├── UserValidator
└── UserMapper
```

Each generated artifact can provide and require symbols:

```text
UserEntity implements User
UserDto implements UserInput
UserMapper maps UserEntity to User
UserResponse contains User
```

The pack owns those generated-role relationships.

## Approved architectural rule

```text
[APPROVED DIRECTION]

- A pack may emit several artifacts from one Schema.
- A template may provide a symbol tied to that Schema.
- Another template may require that symbol.
- Dryv resolves the artifact, symbol, import and dependency.
- The template renders target-language syntax such as `implements`.
- Generated `implements` relationships do not need to become canonical Schema relationships.
- StorageMapping still canonically maps Schema.
```

So yes:

> A template author can generate `TypeX` from Schema X, generate `EntityX` from its StorageMapping, and make `EntityX implements TypeX`. This belongs to pack planning, symbols, dependencies, and template rendering—not to the canonical meaning of Schema inheritance.
