# Research result

I audited representative flows on the **`develop`** branches:

* DefyTickets backend and organiser frontend: the Pool lifecycle.
* Riderescue backend and driver app: the Booking lifecycle.
* Riderescue’s generated Dart SDK from `main`, because the driver app’s `develop` branch explicitly consumes that SDK branch.
* A public NestJS RealWorld application as a conventional manual-code benchmark.

This is a representative architecture audit, not an exhaustive review of every repository file.

## Main conclusion

The most important distinction for Dryv is:

```text
Semantic concept
≠
generated representation of that concept
```

For example:

| Semantic meaning | Representations found in the projects                                                                                 |
| ---------------- | --------------------------------------------------------------------------------------------------------------------- |
| Pool             | entity, interface, create/update DTOs, contract schemas, generated TypeScript types, form, table row                  |
| Booking          | database model, domain interface, summaries, actor-specific detail views, API schemas, generated Dart models, screens |
| Create Pool      | controller method, service method, use case, route contract, generated server action, form submission                 |
| Place Booking    | controller method, service operation, use case, route contract, generated SDK method, frontend controller             |

Therefore, terms such as:

```text
entity
DTO
controller
service
repository
use case
client
form
page
screen
component
```

are usually **generation roles**, not the underlying neutral software concepts.

The stable Dryv concepts are closer to:

```text
schema
field
relationship
projection
operation
input
output
failure
effect
state
transition
policy
event
storage mapping
presentation
workflow
```

---

# 1. How one concept spreads across a project

## DefyTickets Pool

The Pool entity contains persistence concerns: columns, indexes, defaults and TypeORM relationships.

The `IPool` interface repeats the structural fields, then classifies those fields into many meaningful groups:

* readonly;
* frozen after creation;
* immutable;
* creatable;
* updatable;
* sortable;
* searchable;
* filterable;
* selectable;
* editable;
* relationships.

The DTO represents only the accepted create payload, adds validation, transformations and nested time-window input.

The Pool contract defines several distinct projections:

* `PoolPublic`;
* `PoolPartial`;
* `CreatePoolBody`;
* `UpdatePoolBody`;
* `PatchPoolBody`;
* queries;
* route parameters;
* responses.

The generated organiser code then creates TypeScript interfaces, typed routes and server actions from those contract definitions.

Finally, the form and table use only the projections relevant to their presentation. The form exposes selected editable fields and adds UI-specific defaults, labels and conditional controls.  The table selects another subset and adds labels, status colours and formatting.

So the real relationship is:

```text
Pool schema
├── persistence representation
├── public projection
├── create projection
├── update projection
├── query capabilities
├── generated client representations
└── presentation-specific representations
```

It is **not**:

```text
Pool entity
→ copy entity everywhere
```

## Riderescue Booking

Riderescue demonstrates the same pattern more strongly.

The core Booking type defines fields, relationships and lifecycle states.

Separate field collections classify:

* creation fields;
* update fields;
* lifecycle fields;
* public fields;
* relation fields;
* sortable fields;
* searchable fields;
* filter fields;
* date-range fields.

The service interface then defines several intentionally different projections of the same Booking:

* `BookingSummaryView`;
* `DriverBookingDetailView`;
* `WorkerJobDetailView`;
* `CompanyBookingDetailView`;
* `AdminBookingLedgerDetailView`.

This means **projection is a real first-class software concept**. A Booking does not have one universally correct DTO.

Different actors need different representations, permissions, relationships and detail levels.

---

# 2. How operations relate across layers

Consider `placeDriverBooking`.

The controller receives a transport DTO, converts its nested location representation into a domain location and calls the service operation.

The transport DTO defines validation and input encoding.

The service interface defines the neutral operation input and result.

The use case performs the real business process:

```text
validate request
→ create booking
→ create snapshot
→ record event
→ publish domain event
→ begin matching
→ assemble result projection
```

The route contract describes the operation as a transport endpoint with its input, response and access rules.

The generated Dart SDK produces:

* the typed request model;
* typed route parameters;
* the HTTP method;
* result deserialization;
* stable operation identity.

The frontend controller collects screen state and invokes the generated client.

The stable identity is therefore:

```text
Operation: placeDriverBooking
```

These are representations of it:

```text
controller method
service method
use-case method
HTTP route
SDK method
form or screen action
```

Dryv should let templates select the **operation**, then generate whichever representation the pack needs.

It should not require the author to separately describe a controller method, SDK method and form action when they all represent the same operation.

---

# 3. What generation already did well

## Typed clients removed repetitive wiring

The DefyTickets generator produced consistent:

* routes;
* path parameter types;
* query types;
* request-body types;
* response types;
* server actions;
* form-action wrappers.

The Riderescue SDK generated the same type of structure for Dart:

* model imports;
* request objects;
* route invocation;
* response parsing;
* operation IDs.

This is exactly where generation provides high value. The code is structurally repetitive but must remain contractually consistent.

## Generated symbols improved frontend code

The frontends import generated symbols rather than manually recreating API types:

```text
PoolPartial
PoolStatus
CreatePoolBody
DriverBookingDetail
PlaceBookingBody
BookingStatus
```

That reduces manual interface duplication and allows contract changes to become visible during compilation.

## Manual orchestration remained possible

DefyTickets uses generated actions but retains a small hand-written feature layer that decides whether a form performs create or update. It does not recreate routes, DTOs or response envelopes.

That is a healthy generation boundary:

```text
Generate stable structural wiring.
Author product-specific orchestration.
```

---

# 4. Where manual duplication caused drift

## A. Field and relationship drift

`Pool` has a `timeWindow` relationship and exposes it as a selectable/public field, but the explicit Pool relation-key list only contains `event` and `tenant`.

The query DTO also contains names such as:

```text
name
externalId
isUnlimited
```

while the Pool’s main field is `title`, and the shown Pool model does not define `externalId` or `isUnlimited`.

These lists are all trying to describe field capabilities, but because they are manually repeated, they can disagree.

### Dryv lesson

Field capabilities and projections should be declared once as semantic relationships, then queried by templates.

---

## B. Contract and response drift

The Pool controller declares deletion as HTTP 204.

The service returns a `{ deletedId }` object.

The contract defines a `NoContent` response but its deletion route references an API message response instead.

This is exactly the kind of inconsistency DefyTickets later required a large controller-versus-contract audit to detect across its resource contracts.

### Dryv lesson

An operation’s response and status are part of the operation concept. Different templates should consume the same operation definition rather than manually restating it.

---

## C. Lifecycle-policy drift

DefyTickets has an explicit Pool transition table.

But the service’s status method directly writes the requested status without using that transition manager.

The frontend separately defines:

```text
canPause
canResume
canEnd
canDelete
```

using another manually maintained set of conditions.

Three places describe approximately the same lifecycle policy, but none is guaranteed to remain synchronized.

Riderescue shows an even clearer example.

The backend permits driver cancellation only while a booking is:

```text
pending
matching
offered
assigned
```

The Flutter screen’s fallback logic also allows cancellation while `enRoute`.

The backend permits pickup changes only while `pending` or `matching`.

The frontend fallback allows them during `offered` and `assigned` too.

The screen already receives `allowedActions`, but still retains duplicated status-based fallback logic.

### Dryv lesson

State transitions, policies and allowed actions should be explicit concepts.

A presentation should consume an authored or derived allowed-action projection rather than independently reconstructing backend policy.

---

## D. Generated path-token drift

The generated DefyTickets route map contains functions receiving `typeValue`, while the returned path in the inspected attribution routes retains the literal `{type}` token.

This suggests a mismatch between:

```text
semantic route parameter identity
generated function parameter
output path token
```

### Dryv lesson

Path parameters must be typed symbols with stable identity, not strings renamed independently at several generation stages.

---

## E. Dependency and regeneration drift

The current generated Riderescue `PlaceBookingBody` requires `providerCategoryId`.

The driver app’s request builder shown on `develop` constructs that body without supplying `providerCategoryId`.

Because the app declares the SDK through a Git dependency on its `main` branch, this is either:

* a compile-time mismatch with the current SDK;
* or evidence that the resolved dependency is behind and regeneration/dependency resolution is not synchronized.

### Dryv lesson

Generated code helps expose drift, but only when:

```text
source definition
generated package
consumer lock state
```

are traceable to the same version.

Generation does not eliminate consistency problems by itself. Reproducible planning and ownership are required.

---

## F. Mapping drift

Riderescue transport represents a location as:

```text
BookingLocationInputDto
└── point
    ├── type
    └── coordinates
```

The domain model uses:

```text
IBookingLocation
├── type
├── coordinates
├── address
└── placeId
```

The controller manually maps between them.

This mapping is legitimate, but it is an explicit semantic transformation. It should not be inferred merely because some field names resemble one another.

### Dryv lesson

Mappings between projections should be first-class and inspectable.

---

# 5. Public benchmark

The public NestJS RealWorld application follows the same broad structure:

```text
controller
→ DTO
→ service
→ entity/repository
```

But it also shows typical manual weaknesses:

* untyped query and parameter values;
* one create DTO reused for update;
* `any` used in update logic;
* a TODO because changing the title does not update the slug;
* manual DTO-to-entity property assignment.

This confirms that the drift seen in Riderescue and DefyTickets is not unusual. Layered applications repeatedly represent the same concepts, and manual synchronization becomes difficult as projects evolve.

---

# 6. What can be templated efficiently

## High-confidence generation

These are structurally repetitive and connected to explicit semantic facts:

* persistence entities and models;
* interfaces and language types;
* request and response projections;
* validators;
* route definitions;
* controller or resolver shells;
* service interfaces;
* service delegation shells;
* generic repository configuration;
* field capability lists;
* SDK clients;
* server actions;
* serializers;
* import and export wiring;
* barrels;
* documentation;
* contract tests;
* basic form and table structures when a presentation is explicitly authored.

## Partially generatable

These require explicit authored meaning before templates can generate them safely:

* schema-to-schema mappings;
* state-transition enforcement;
* allowed-action calculation;
* access policies;
* event publication;
* cache invalidation;
* transaction boundaries;
* actor-specific views;
* form layout and conditional fields;
* workflow orchestration.

## Must not be guessed from a schema

Dryv should not infer:

* create fields from every non-readonly entity field;
* update fields from create fields;
* public fields from persistence fields;
* forms from DTOs alone;
* lifecycle actions from enum values;
* route methods from operation names;
* relation-loading rules;
* actor permissions;
* domain transformations;
* business transaction steps.

Those must be authored or explicitly derived from authored rules.

---

# 7. Proposed concept structure

Based on the benchmark, the concept-review order should begin with meaning rather than framework files.

## Semantic concepts — proposed, not approved

```text
Schema
Field
Relationship
Projection
Mapping
Operation
Input
Output
Failure
Effect
State
Transition
Policy
Allowed action
Event
Storage mapping
Presentation
Workflow
```

## Output roles — proposed, not canonical concepts

```text
Entity
Model
DTO
Controller
Service
Repository
Use case
Client
Page
Screen
Component
Form
Table
Barrel
```

A pack could select a semantic concept and emit one of these roles.

Example:

```text
Schema: Pool
    ↓
TypeORM pack emits entity
API pack emits public DTO
TypeScript-client pack emits interface
Admin-UI pack emits form
Admin-UI pack emits table configuration
```

The output role belongs to the pack. The Pool’s meaning does not change.

---

# 8. Refined review pipeline

Your original sequence is sound. The evidence suggests one important addition:

```text
Concept
→ Authorability
→ Relationships and projections
→ Selectability
→ Templatability
→ Emitability
→ Composability
→ Auditability
```

### Why relationships and projections should be reviewed early

Before deciding whether `Booking` is selectable, we need to know whether the template wants:

* the complete Booking;
* the public Booking;
* the driver detail projection;
* the worker job projection;
* the create input;
* the list projection.

Without an explicit projection model, selection keywords will become overloaded with framework names such as:

```text
DTO
entity
model
public
preview
response
```

That would move target-specific vocabulary into the canonical selector system.

---

# 9. Selection-design implications

The research supports two distinct selection needs.

## Semantic selection

Templates select authored or derived meaning:

```text
schemas
projections
operations
events
presentations
workflows
```

## Planned-artifact selection

Some templates, especially barrels and indexes, select outputs already planned by other templates:

```text
artifacts
symbols
exports
```

These should not be confused.

For example:

```text
Generate one DTO for each public projection
```

is semantic selection.

```text
Export all DTO symbols emitted in this module
```

is artifact selection.

Both are needed, but they operate at different stages.

This distinction is currently **PROPOSED**, not approved.

---

# Decision checklist

## Already approved

```text
[APPROVED] Eliminate language adapters
[APPROVED] Templates own target-language syntax
[APPROVED] Dryv resolves symbols, artifacts, paths and dependencies
```

## Recorded from the previous discussion

```text
[AGREED FOUNDATION] Barrels are artifacts that re-export symbols
[AGREED FOUNDATION] Import relativity uses the chosen direct artifact or barrel
```

## Research-supported proposals awaiting your approval

```text
[PROPOSED] Separate semantic concepts from generated output roles
[PROPOSED] Treat projections as first-class concepts
[PROPOSED] Treat mappings as explicit concepts
[PROPOSED] Treat operations as shared identities across controllers,
           services, use cases, clients and UI actions
[PROPOSED] Treat states, transitions and allowed actions as explicit meaning
[PROPOSED] Make presentations explicit rather than inferred from schemas
[PROPOSED] Separate semantic selection from planned-artifact selection
[PROPOSED] Use the review chain:
           Concept → Authorability → Relationships/Projections
           → Selectability → Templatability → Emitability
           → Composability → Auditability
```

## Still unreviewed

```text
[UNREVIEWED] Final canonical concept catalog
[UNREVIEWED] Which concepts are directly selectable
[UNREVIEWED] Selection keywords
[UNREVIEWED] Query and filter vocabulary
[UNREVIEWED] Template variable names
[UNREVIEWED] Output-role vocabulary
```

The first human decision should be whether to approve this foundation:

> **Dryv selects semantic concepts such as schemas, projections and operations; packs emit representations such as entities, DTOs, controllers, clients, forms and screens.**


# Research verdict

The evidence across DefyTickets, Riderescue, Go, PHP, C#, Java, Swift, and Android changes the concept model in an important way:

> **Dryv should model software definitions and relationships—not framework files and not live runtime records.**

A reliable cross-layer flow looks like:

```text
User intent / external request
    ↓
Command or query
    ↓
Operation
    ↓
State change and declared consequences
    ↓
Domain event
    ↓
Publication / subscription
    ↓
Handler, workflow, projection, notification, or integration
    ↓
Frontend state and presentation
```

An outbox row, delivery attempt, queue job, workflow execution, controller class, reducer, or notification worker is a **representation or runtime record** generated around that meaning.

---

# 1. What DefyTickets reveals

## Events are not one concept

DefyTickets currently separates:

```text
Event definition
Event occurrence
Outbox publication
Event handler
Handler execution
Retry attempt
Parent event status
Secure payload
```

The outbox event carries event type, aggregate identity, payload, schema version, trigger, status and timestamps.

Each handler receives a separate execution record containing handler identity, priority, attempts, locks, timing and failure details.

The executor discovers matching handlers, creates one execution per handler, executes them, independently retries them and derives the parent event status from all child executions. It can represent partial failure rather than incorrectly saying the entire event either succeeded or failed.

This gives the correct conceptual graph:

```text
Event occurrence
    ├── delivered to handler A
    │       └── handler execution A
    ├── delivered to handler B
    │       └── handler execution B
    └── delivered to handler C
            └── handler execution C
```

Therefore:

* an **event** is a fact;
* a **subscription** connects an event to a reaction;
* a **handler** implements that reaction;
* a **handler execution** is a runtime occurrence;
* an **outbox record** is a delivery mechanism.

They must not be collapsed into one `event` concept.

## Transaction boundaries are meaningful

The DefyTickets publisher writes an outbox event inside the caller’s existing transaction when available. It deliberately avoids enqueueing before that transaction commits because a worker could otherwise attempt to read an uncommitted event. Recovery later finds and enqueues it.

This suggests a neutral relationship:

```text
Operation
    changes state
    emits event
    requires atomic publication
```

But the generated implementation may be:

```text
TypeORM transaction + outbox table + BullMQ recovery
```

Dryv should represent the **reliability requirement**, while the pack represents the implementation.

## Event schema evolution matters

DefyTickets records an `eventSchemaVersion` and resolves it from an event-definition registry.

CloudEvents independently distinguishes event type, event identity, source, occurrence time, data content type and data schema. It also recommends changing the event type and schema identity appropriately when payloads evolve incompatibly. ([GitHub][1])

This means an event needs:

```text
identity
name/type
owner/source
subject
payload schema
schema version
occurrence time
```

Transport protocol, broker and serialization remain bindings.

---

# 2. What Riderescue reveals

Riderescue uses a simpler durable event model:

```text
Event
→ one outbox record
→ asynchronous emitter
→ all listeners
→ one delivered/failed/dead-letter status
```

It stores attempts, backoff, locks and delivery status on the event record itself.  Recovery claims stale or failed records using leases and bounded batches.

This is valid, but it has different semantics from DefyTickets.

With a single event-level delivery record, when one listener fails after another has succeeded, retrying the event may invoke the successful listener again. Watermill documents the same redelivery risk when grouped handlers share message acknowledgement. ([Watermill][2])

Therefore, Dryv must not silently assume either:

```text
one delivery record per event
```

or:

```text
one delivery record per subscription
```

That is a deliberate **delivery policy**.

## Commands and events are being mixed

Riderescue handles `WorkerAssignmentCreated`, then publishes `NotificationRequested`.

`WorkerAssignmentCreated` is clearly a fact:

```text
Something happened.
```

`NotificationRequested` is closer to an instruction:

```text
Please perform this work.
```

AsyncAPI explicitly distinguishes messages as commands, queries or events: an event describes something that already occurred, while not every message is an event. ([AsyncAPI][3])

This suggests the vocabulary:

```text
Command:
  requests a change or effect

Query:
  requests information

Event:
  reports a fact that occurred
```

An operation may be invoked by a command and may emit one or more events.

---

# 3. Notifications are a small system, not one output

DefyTickets separates several notification concepts:

```text
Notification request
Notification definition
Notification content version
Recipient
Channel
Provider
Delivery attempt
Render data
Secure render data
Schedule
Status
```

The notification request records source event information, template definition/version, implementation, channel, category, priority, scheduling, idempotency and source traceability.

Each delivery attempt separately records recipient, provider, channel, attempt number, provider identifiers and failure details.

The sender first creates a request, then either queues it or performs recipient deliveries inline, producing `sent`, `failed`, or `partial_failed` aggregate results.

Request creation also handles:

* recipient-specific data;
* duplicate recipients;
* idempotency;
* scheduling;
* secure variables;
* redacted persisted data;
* variable persistence policies;
* template resolution and versioning.

Laravel independently models a semantic notification that can be delivered through email, database, broadcast and custom channels. Queued notifications may produce separate jobs for recipient-channel combinations, and dispatch timing must account for database transaction commit. ([Laravel][4])

Apple similarly distinguishes notification content, trigger, delivery and user actions; remote transport through APNs is separate from the notification’s application meaning. ([Apple Developer][5])

## Proposed notification structure

```text
Notification definition
├── purpose/category
├── data schema
├── audience
├── supported channels
├── content variants
├── actions/deep links
├── preference policy
└── security/persistence policy

Notification request
├── definition reference
├── source/cause
├── recipients or audience
├── render data
├── schedule
└── idempotency identity

Delivery
├── recipient
├── channel
├── provider
├── attempts
└── result
```

Only the **definition and its semantic relationships** belong in authored Runtime IR.

Notification requests and delivery attempts are live runtime data. Packs may generate their database models, workers and clients.

## Vocabulary warning

Dryv already uses **template** to mean a code-generation template.

Calling an email body a `notification template` inside the same canonical vocabulary will create ambiguity.

A clearer neutral term should be reviewed, such as:

```text
notification content
message content
notification presentation
```

No term is approved yet.

---

# 4. Workflows are broader than ordered steps

DefyTickets already contains a strong distinction:

```text
Workflow definition
≠
Workflow execution
```

The definition contains defaults, allowed triggers, execution mode, timeout, retry and dead-letter policies.

The execution record contains current state, checkpointed steps, context, result, failures, timing, queue identity, tenant and initiator.

The checkout workflow is currently an ordered sequence:

```text
prepare context
→ validate coupon
→ initialize inventory
→ create payment intent
→ finalize response
```

Its steps can contain conditions and rollback behavior.  The executor checkpoints progress, resumes unfinished work, observes cancellation, enforces timeouts, skips conditional steps and compensates completed steps after failure.

This is a good foundation, but it is only one workflow shape.

## Public PHP evidence

Symfony distinguishes:

* places;
* current marking;
* transitions;
* transition guards;
* workflow lifecycle events;
* workflow models that may occupy several places simultaneously;
* state machines that permit only one current place. ([Symfony][6])

Sylius attaches business effects to completed workflow transitions. One listener holds inventory, while another gives inventory back on a different transition.

This is not merely:

```text
step 1
step 2
step 3
```

It is:

```text
state/place
    ↓ transition
guard
    ↓
lifecycle event
    ↓
business effect
```

## Workflow standards and durable systems

SCXML supports hierarchical and parallel states, event-driven transitions and conditional transitions. ([W3C][7])

BPMN distinguishes events, activities, gateways, sequence flows, parallel paths, exception flows, message waits and compensation. ([OMG Issue Tracker][8])

The CNCF Serverless Workflow specification includes event-driven orchestration, tasks, retries, timeouts and fault handling rather than only linear steps. ([Serverless Workflow][9])

Temporal’s durable model persists workflow execution and advances it through commands such as scheduling activities, starting timers, starting children and signalling other workflows. Queries inspect a workflow without advancing it. ([GitHub][10])

## Required workflow distinctions

Dryv should eventually be able to describe:

```text
Workflow definition
Workflow input and output
Trigger
Task/activity
State/place
Transition
Condition
Guard
Branch
Join
Parallel path
Iteration
Wait
Timer
External signal
Child workflow
Checkpoint
Cancellation
Timeout
Retry policy
Compensation
Completion/failure event
```

Not every workflow will use every capability.

A simple workflow should remain simple:

```text
workflow
  step
  step
  step
```

But the canonical model must not make branching, waiting or parallel execution impossible.

---

# 5. Go evidence: commands, events and handlers

Watermill’s Go implementation separately constructs command buses, event buses, command processors and event processors. It also treats routing/topic generation, publisher selection, subscribers and marshaling as configurable infrastructure.

Its CQRS model makes an important cardinality distinction:

```text
Command → exactly one command handler
Event   → zero or many event handlers
```

Event handlers may update aggregates, create read models, invoke process managers or cause further events. ([Watermill][2])

This strongly supports:

* command and event as different concepts;
* handler binding as a first-class relationship;
* read-model projection as a first-class concept;
* process manager or saga as a workflow/orchestration concept;
* topic, broker and router as implementation bindings.

---

# 6. C# evidence: domain events and integration events

Microsoft’s eShop separates integration-event handlers by service and event type. The same business event may have handlers in ordering, catalog, basket, payment, webhooks and frontend-facing services.

Its integration-event log stores:

* event ID;
* concrete event type;
* serialized event content;
* creation time;
* publication state;
* send count;
* originating transaction ID.

The log service saves the event using the same database transaction, retrieves unpublished entries in creation order and marks them in progress, published or failed.

Microsoft’s architecture guidance distinguishes internal domain events from integration events shared between services, where eventual consistency and idempotent consumers are expected. ([Microsoft Learn][11])

This suggests:

```text
Domain event:
  meaningful inside an ownership boundary

Integration event:
  externally published contract derived from a domain occurrence
```

They may share a payload, but they are not necessarily the same contract.

---

# 7. Java evidence: publication is per listener

Spring Modulith writes one publication entry for each transactional event listener as part of the original business transaction. A successful listener marks its entry completed; an unsuccessful one leaves an incomplete publication that can be retried. ([Home][12])

This independently validates the DefyTickets per-handler execution design.

Spring Modulith also separates:

```text
application event
event publication
target listener
publication completion
externalized message
broker routing
```

It supports mapping an internal event into a different externally published payload and selecting only specific events for externalization. ([Home][12])

Therefore, Dryv should not assume that publishing an event means serializing the internal event object unchanged.

A first-class **mapping** may connect:

```text
DomainEvent → IntegrationEvent
```

---

# 8. Swift and frontend evidence

Swift’s Composable Architecture models a feature through:

```text
State
Action
Reducer
Effect
Store
View
```

Actions include user interaction, notifications, external events and responses from effects. Reducers transform state and launch effects such as API requests.

The production Swift application isowords follows this model. Its Settings feature has:

* persistent feature state;
* user actions;
* notification authorization responses;
* API effects;
* settings mutations;
* child feature composition;
* alert and navigation behavior.

Android’s official architecture guidance reaches the same structure through different vocabulary:

```text
User event
→ state holder
→ business/data operation
→ new UI state
→ rendered UI
```

It explicitly distinguishes transient events from durable state and recommends unidirectional data flow and a single source of truth. ([Android Developers][13])

## Backend–frontend relationship

The common cross-platform flow is:

```text
Frontend action or intent
    ↓
Command / operation
    ↓
Backend result and domain events
    ↓
API response, realtime event, or notification
    ↓
Frontend effect result
    ↓
Feature state transition
    ↓
Page, screen, or component renders state
```

Therefore:

* `page`, `screen`, `View`, `ViewModel`, `Reducer` and `Store` are output roles;
* feature state, user action, effect relationship and presentation projection contain reusable meaning.

---

# 9. The strongest architectural boundary for Dryv

The research supports four different categories.

## A. Authored semantic definitions

These are candidates for canonical Runtime IR:

```text
schema
field
relationship
projection
mapping
operation
command
query
event
event payload
subscription
policy
state model
transition
workflow
workflow task
notification definition
audience
presentation
feature action
```

Their exact names and selectability remain unapproved.

## B. Semantic relationships and policies

Examples:

```text
operation consumes input
operation returns output
operation emits event
event belongs to an aggregate
event maps to integration event
subscription reacts to event
subscription starts workflow
subscription updates projection
subscription requests notification
transition moves between states
transition requires guard
workflow task produces output
workflow failure invokes compensation
notification targets audience
presentation action invokes operation
```

These relationships are more important than the generated class names.

## C. Generated output roles

These belong to packs:

```text
entity
database model
DTO
controller
resolver
service
repository
use case
event class
event handler class
subscriber
producer
outbox entity
queue worker
workflow executor
notification sender
SDK client
reducer
ViewModel
page
screen
component
form
barrel
```

A pack selects semantic definitions and emits these representations.

## D. Runtime execution records

These normally should **not** be authored Runtime IR concepts:

```text
outbox row
handler attempt
queue job
workflow run
workflow checkpoint
notification request instance
recipient instance
delivery attempt
provider response
lock or lease
retry occurrence
```

Packs may generate schemas and code for these records, but actual runtime instances belong to the generated application.

This boundary prevents Dryv Runtime IR from becoming an event broker, workflow database or notification runtime.

---

# 10. Concepts we were missing or under-modelling

## High-confidence additions to review

### Command

A request to perform work.

```text
CancelOrder
PlaceBooking
SendInvitation
```

### Query

A request to return information without expressing a business occurrence.

```text
FindOrders
GetBooking
ListAvailablePools
```

### Event

A fact that already occurred.

```text
OrderCancelled
BookingPlaced
TicketsIssued
```

### Subscription

A declared reaction:

```text
when OrderCancelled
run ReleaseInventory
```

The generated representation might be a handler, listener, subscriber, reducer case or webhook consumer.

### Event envelope

Neutral contextual identity:

```text
event ID
type
source/owner
subject
occurredAt
payload schema/version
correlation identity
causation identity
tenant/aggregate context
```

### Integration event

An externally consumable event contract, potentially mapped from an internal domain event.

### Read model

A projection maintained for efficient reading, reporting, search or presentation.

### Audience

A semantic recipient group:

```text
customer
organiser
assigned worker
tenant administrators
specific users
```

### Delivery policy

A neutral reliability requirement:

```text
durable or transient
ordering scope
retry policy
failure isolation
idempotency requirement
concurrency policy
```

The broker-specific implementation remains pack configuration.

---

# 11. Concepts that should not be prematurely unified

## Domain state versus workflow state

An Order status lifecycle and a checkout orchestration are related but different:

```text
Order lifecycle:
  pending → paid → fulfilled

Checkout workflow:
  validate → reserve → charge → finalize
```

## Workflow effect versus frontend effect

A frontend `Effect` may mean an API call or navigation.

A workflow effect may mean reserving inventory or sending payment.

An operation’s declared effect may mean that it changes storage or emits an event.

Using one unrestricted `effect` object for all three would become vague.

## Domain event versus UI event

Backend:

```text
OrderPaid
```

is a historical fact.

Frontend:

```text
PayButtonTapped
```

is a user action or intent.

Using `event` for both makes selection and tracing ambiguous. Dryv should likely reserve `event` for facts and use `action` or `intent` for presentation interaction.

---

# 12. What should be generated

With explicit concepts and relationships, packs can efficiently generate:

```text
event payload classes
CloudEvents-style envelopes
command/query objects
command and event handlers
subscriber registration
outbox tables and repositories
event serializers
retry workers
integration-event mappings
workflow definitions and executors
workflow state schemas
notification request/delivery models
channel senders
frontend API clients
realtime event listeners
feature actions and reducers
UI state models
forms, pages and screens
tests and trace documentation
```

But Dryv must not guess:

* which operation emits which event;
* whether an event is internal or external;
* which subscribers must be durable;
* whether retries are safe;
* how idempotency is calculated;
* whether handlers may run concurrently;
* which workflow steps compensate others;
* which notification audiences and channels are valid;
* which frontend actions are allowed in each state.

Those are authored decisions.

---

# Proposed concept graph

```text
Operation
├── invokedBy: Command | Query | UserAction | Trigger
├── consumes: Input
├── returns: Output
├── requires: Policy
├── changes: Aggregate/State
└── emits: DomainEvent

DomainEvent
├── payload: Schema
├── subject: Aggregate
├── version
├── causedBy
├── correlatedWith
├── mappedTo: IntegrationEvent
└── subscriptions: Subscription[]

Subscription
├── consumes: Event
├── condition
├── deliveryPolicy
└── reaction:
    ├── Operation
    ├── Command
    ├── Workflow
    ├── Projection
    ├── Notification
    └── IntegrationPublication

Workflow
├── input/output
├── triggers
├── tasks
├── states/transitions
├── conditions/guards
├── branches/joins
├── waits/timers/signals
├── retries/timeouts
└── compensation

Notification
├── dataSchema
├── audience
├── content
├── channels
├── preferences
├── actions/deepLinks
└── securityPolicy

PresentationFeature
├── state
├── actions
├── projections
├── operations
└── presentationEffects
```

This is a research-supported proposal, not an approved final IR.

---

# Checklist update

## Approved

```text
[APPROVED] Eliminate language adapters
[APPROVED] Templates own target-language syntax
[APPROVED] Dryv resolves artifacts, symbols, paths and dependencies
[APPROVED] Barrels are artifacts that re-export symbols
[APPROVED] Relativity is calculated against the selected provider or barrel
```

## Strong proposals awaiting approval

```text
[PROPOSED] Separate semantic definitions from generated output roles
[PROPOSED] Separate authored definitions from runtime execution records

[PROPOSED] Distinguish command, query and event
[PROPOSED] Reserve event for a fact that occurred
[PROPOSED] Represent subscription as Event → Reaction relationship
[PROPOSED] Distinguish domain event from integration event
[PROPOSED] Support explicit DomainEvent → IntegrationEvent mappings
[PROPOSED] Give events a neutral versioned envelope
[PROPOSED] Treat read models as projections

[PROPOSED] Represent reliability through neutral delivery policies
[PROPOSED] Do not claim automatic exactly-once delivery
[PROPOSED] Represent idempotency, ordering, concurrency and failure isolation

[PROPOSED] Separate notification definition, audience and channel
[PROPOSED] Keep notification request/delivery instances outside authored IR
[PROPOSED] Avoid using unqualified “template” for notification content

[PROPOSED] Separate workflow definition from workflow execution
[PROPOSED] Support more than ordered workflows
[PROPOSED] Represent conditions, guards, branches, joins and parallel paths
[PROPOSED] Represent waits, timers, signals and child workflows
[PROPOSED] Distinguish retry from compensation
[PROPOSED] Represent checkpoints and resumability as workflow policies

[PROPOSED] Represent frontend feature state and actions
[PROPOSED] Distinguish UI action from domain event
[PROPOSED] Treat pages, screens, reducers and ViewModels as output roles
```

## Still unreviewed

```text
[UNREVIEWED] Exact canonical names
[UNREVIEWED] Whether command and query are roots or operation facets
[UNREVIEWED] Whether subscriptions are directly selectable
[UNREVIEWED] Whether workflow tasks and transitions are directly selectable
[UNREVIEWED] Whether notification definitions are directly selectable
[UNREVIEWED] Exact delivery-policy vocabulary
[UNREVIEWED] Exact frontend feature vocabulary
```

# Most important next decision

Before selecting keywords, approve or reject this boundary:

> **Dryv Runtime IR describes definitions, relationships and required behavior. Outbox rows, handler attempts, workflow runs, notification deliveries and queue jobs are runtime representations generated by packs—not authored canonical IR instances.**

That decision prevents the canonical model from accidentally becoming tied to NestJS, BullMQ, TypeORM, Temporal, Symfony Workflow, Swift reducers, or any other implementation.

[1]: https://github.com/cloudevents/spec/blob/main/cloudevents/spec.md?utm_source=chatgpt.com "spec/cloudevents/spec.md at main · cloudevents/spec · GitHub"
[2]: https://watermill.io/docs/cqrs/?utm_source=chatgpt.com "CQRS Component | Watermill | Event-Driven in Go"
[3]: https://www.asyncapi.com/docs/concepts/message?utm_source=chatgpt.com "Message | AsyncAPI Initiative for event-driven APIs"
[4]: https://laravel.com/docs/12.x/notifications?utm_source=chatgpt.com "Notifications | Laravel 12.x - The clean stack for Artisans and agents"
[5]: https://developer.apple.com/documentation/usernotifications/handling-notifications-and-notification-related-actions?utm_source=chatgpt.com "Handling notifications and notification-related actions | Apple Developer Documentation"
[6]: https://symfony.com/doc/current/components/workflow.html?utm_source=chatgpt.com "The Workflow Component (Symfony Docs)"
[7]: https://www.w3.org/TR/scxml/?utm_source=chatgpt.com "State Chart XML (SCXML): State Machine Notation for Control Abstraction"
[8]: https://issues.omg.org/issues/spec/BPMN/2.0/fixed?utm_source=chatgpt.com "BPMN — Closed Issues - OMG Issue Tracker"
[9]: https://serverlessworkflow.io/blog/releases/release-100/?utm_source=chatgpt.com "Open Workflow Specification - Serverless Workflow 1.0.0 Release"
[10]: https://github.com/temporalio/temporal/blob/main/docs/architecture/README.md?utm_source=chatgpt.com "temporal/docs/architecture/README.md at main · temporalio/temporal · GitHub"
[11]: https://learn.microsoft.com/en-us/azure/architecture/databases/guide/transactional-out-box-cosmos?utm_source=chatgpt.com "Implement the Transactional Outbox Pattern by Using Azure Cosmos DB - Azure Architecture Center | Microsoft Learn"
[12]: https://docs.spring.io/spring-modulith/reference/events.html?utm_source=chatgpt.com "Working with Application Events :: Spring Modulith"
[13]: https://developer.android.com/topic/architecture/ui-layer/stateholders?hl=en&utm_source=chatgpt.com "State holders and UI state  |  App architecture  |  Android Developers"



Correct.

The **relationship owner must declare the action**. The Event should not list who emits, handles, subscribes, or hooks into it.

```text
Event
├── name
└── schema
```

Then other concepts declare their relationship:

```text
Emitter
└── emits: Event

Handler
└── handles: Event

Subscriber
└── subscribesTo: Event

Hook
├── before: Operation
└── after: Operation
```

These may be operation roles rather than separate heavy concepts:

```text
Operation
├── emits: Event[]
├── handles: Event[]
├── subscribesTo: Event[]
├── runsBefore: Operation[]
└── runsAfter: Operation[]
```

The direction is:

```text
Operation → Event
```

Not:

```text
Event → all related operations
```

Dryv Runtime may build reverse indexes for queries and audit:

```text
Which operations emit this event?
Which operations handle this event?
```

But those are **derived relationships**, not authored fields on the Event.

### Checklist correction

```text
[APPROVED] Relationship owners declare their actions.
[APPROVED] Events do not author reverse references.
[APPROVED] Runtime may derive reverse indexes for selection and audit.
[REJECTED] Event.emittedBy
[REJECTED] Event.handledBy
[REJECTED] Event.subscribers
[REJECTED] Event.beforeHooks
[REJECTED] Event.afterHooks
```


Yes, that is correct.

## Authoring

The relationship is authored only from the active side:

```text
Operation.emits(event)
Operation.handles(event)
Operation.subscribesTo(event)
Hook.before(operation)
Hook.after(operation)
```

The Event does not duplicate those relationships.

## Runtime and templating

Dryv resolves reverse relationships and can expose them to an Event template:

```text
event.emitters
event.handlers
event.subscribers
event.beforeHooks
event.afterHooks
```

These lists are **derived template context**, not authored Event fields.

Example:

```jinja
{% for handler in event.handlers %}
  {{ handler.name }}
{% endfor %}
```

This supports generating:

* event registries;
* subscriber registration;
* handler maps;
* documentation;
* dependency wiring;
* tests;
* audit reports.

The lists should have deterministic ordering, such as authored order followed by stable semantic ID.

## Approved distinction

```text
[APPROVED] Relationships are authored from their owning side.
[APPROVED] Runtime derives reverse relationship indexes.
[APPROVED] Templates may receive derived relationship lists.
[APPROVED] Derived template context does not alter canonical authorship.
```
