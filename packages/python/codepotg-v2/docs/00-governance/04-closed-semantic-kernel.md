# Closed semantic kernel and template-context contract

This document defines the approved semantic model for CodepotG v2. It is subordinate only to `00-approved-architecture.md` and overrides older examples that use `resource`, `model`, `entity`, `frontend`, `ui`, open-ended facets, or arbitrary graph queries as neutral CodepotG concepts.

## 1. Closed kernel rule

CodepotG has a closed, typed, versioned semantic kernel.

- Every supported semantic object, relation, value, facet, selector, validation rule, and template-context property is defined by CodepotG.
- Source adapters translate source formats into this known kernel.
- Packs and templates consume this known kernel.
- Source adapters, packs, templates, language adapters, and third-party plugins cannot add semantic node kinds, relations, facets, selector grammar, or template-context properties.
- Unknown source metadata may be preserved only through bounded immutable `extensions`, `raw`, and provenance values. Preserving unknown data does not make it part of the semantic kernel.
- Growth means an intentional kernel change with typed models, validation, selectors, contexts, fixtures, documentation, compatibility rules, and a behavior/IR version update.

The internal implementation may use graph indexes for references, impact analysis, workflows, generated dependencies, and traversal. The public IR and template contexts remain typed objects rather than generic `node.kind`, `edge.relation`, or string-keyed fact bags.

## 2. Kernel topology

The primary semantic root is:

```text
contract
└── groups
    └── group
        ├── name
        ├── path
        ├── schemas
        ├── operations
        ├── views
        ├── storage
        │   └── mappings
        ├── workflows
        ├── policies
        ├── events
        ├── groups
        ├── facets
        ├── documentation
        ├── extensions
        └── raw
```

`group` is the neutral organizing concept. It does not mean REST resource, service, module, feature, bounded context, namespace, or package. A template may generate any of those output forms from a group.

The ordering rule is always outer-to-inner:

```text
group.operations
operation.inputs
operation.facets.http
workflow.steps
step.compensation.operation
view.triggers
storage.mapping.schema
```

Do not expose reversed roots such as `http.groups`, `events.operations`, `access.operations`, or `storage.groups`.

## 3. Schemas describe structure

`schema.kind` is structural only. Initial kinds are:

```text
primitive
literal
enum
object
array
map
tuple
union
intersection
alias
unknown
```

The following are not schema kinds:

```text
model
entity
request
response
input
output
class
interface
type
struct
record
trait
```

Class, interface, type, struct, record, and similar words describe generated syntax chosen by templates.

A source may explicitly assign a controlled kernel role such as `dto` to a schema. A DTO remains a schema; `dto` is not a parallel object hierarchy. Input and output direction belongs to an operation's schema use, not permanently to the schema, because the same schema may be reused in both directions.

A schema field exposes semantic facts and presence-aware constraints, for example:

```text
field.required
field.optional
field.nullable
field.readonly
field.has_max_length
field.max_length
field.constraints.max_length.is_set
field.constraints.max_length.value
field.constraints.max_length.origin
```

Templates decide whether these facts become TypeScript modifiers, Dart modifiers, Zod expressions, Joi rules, class-validator decorators, SQL constraints, documentation, or nothing.

## 4. Operations describe executable behavior

The neutral operation contract is:

```text
operation
├── name
├── inputs
├── outputs
├── failures
├── effects
├── facets
├── documentation
├── extensions
└── raw
```

Meaning:

- `inputs` are data required to invoke the behavior;
- `outputs` are successful direct results;
- `failures` are declared failure possibilities;
- `effects` are consequences beyond the direct return value;
- `facets` are kernel-defined typed perspectives on the operation.

An operation input or output is a schema-use record. It references a schema by semantic identity and carries use-specific facts. HTTP query/path/header/body placement belongs to the HTTP facet and references these neutral uses; it does not redefine the operation core.

## 5. Known facets only

Facets organize known domain-specific facts around known semantic objects. They are not a plugin extension mechanism.

The initially approved operation facets are:

```text
operation.facets.http
operation.facets.access
operation.facets.trigger
operation.facets.execution
operation.facets.events
```

Approved workflow facets are:

```text
workflow.facets.access
workflow.facets.trigger
workflow.facets.execution
workflow.facets.events
```

Approved group/view facet locations are documented by their typed contracts when implemented. Unknown facet names are errors. A source adapter may preserve unknown source metadata in bounded extensions but cannot turn it into a new facet.

### HTTP facet

The HTTP facet contains transport facts such as method, path, request bindings, responses, status codes, media types, headers, and deprecation. Templates write NestJS, Express, Spring, client, test, or documentation syntax.

### Trigger facet

A listener is normally an operation with a trigger facet. Known trigger forms may include event, schedule, interaction, storage, and system triggers. An HTTP endpoint uses the HTTP facet; the kernel must not duplicate the same HTTP binding under two unrelated paths.

### Access facet

Reusable policies live under `group.policies`. Application of access rules lives under typed access facets such as:

```text
group.facets.access
operation.facets.access
workflow.facets.access
view.facets.access
```

Access contexts expose declared and effective values so templates do not implement inheritance themselves:

```text
operation.facets.access.declared
operation.facets.access.effective
```

Policy facts may include public/authenticated state, roles, permissions, scopes, ownership conditions, contextual conditions, and referenced policies. CodepotG validates and resolves these facts; templates author guards, decorators, middleware, policy files, or documentation.

### Execution facet and hooks

Supporting behavior around one operation is represented through:

```text
operation.facets.execution.before
operation.facets.execution.around
operation.facets.execution.after_success
operation.facets.execution.after_failure
operation.facets.execution.after_complete
```

A hook entry references an ordinary operation and carries order, condition, input/output bindings, and stop/failure behavior. Hooks are not a separate open-ended executable hierarchy. Group execution defaults may be resolved into declared/effective operation execution contexts.

## 6. Storage mappings

Persistence is represented by:

```text
group.storage.mappings
```

A storage mapping connects a schema to storage facts:

```text
storage mapping
├── name
├── schema
├── store
├── fields
├── keys
├── indexes
├── relations
├── constraints
├── documentation
├── extensions
└── raw
```

`entity` is not a neutral kernel object. A TypeORM, JPA, Doctrine, SQLAlchemy, or other pack may generate an `Entity` class from a storage mapping, but the emitted term belongs to the template.

## 7. Views and interaction

A view is a renderable or navigable interaction unit without assuming web, mobile, desktop, terminal, kiosk, or a particular framework:

```text
group.views
view.parts
view.triggers
view.flows
view.facets.access
```

A trigger may reference an operation. The usual causal chain is:

```text
view trigger
→ operation
→ operation effect
→ event
```

`frontend`, `ui`, `screen`, `page`, `component`, and `widget` are not top-level neutral kernel vocabularies. Source-specific terms may normalize into views/parts or remain in provenance. Templates choose whether a view becomes a React page, Flutter widget tree, desktop scene, form, documentation page, or another artifact.

## 8. Events

Reusable event declarations live under:

```text
group.events
```

An event describes an occurrence and its payload/context. The kernel distinguishes occurrence from delivery:

```text
operation.effects.events
```

means the operation causes an event occurrence, while:

```text
operation.facets.events
```

contains known publication/consumption/channel/binding facts, and:

```text
operation.facets.trigger.event
```

means an event starts the listener operation.

Transport-specific values such as Kafka or AMQP bindings may exist only when represented by a known typed kernel contract. Templates author all producer, consumer, broker, local-event, webhook, or documentation syntax.

## 9. Workflows and compensation

A workflow is a first-class orchestration object:

```text
group.workflows
workflow.inputs
workflow.outputs
workflow.steps
workflow.transitions
workflow.failures
workflow.effects
workflow.facets
```

A workflow step may perform one forward operation and may optionally define one compensation operation:

```text
step.operation
step.compensation.operation
```

Compensation is optional and is not assumed to be an exact inverse. Examples include reserve/release, charge/refund, issue/cancel, or no compensation for an irreversible notification.

A compensation record may include input mappings, condition, retry, timeout, order, and failure policy. Default workflow compensation normally applies to successfully completed steps in reverse completion order. The template decides how to implement this using a plain service, Temporal, Step Functions, BullMQ, a saga, or another runtime.

Known step structures may include operation, decision, parallel, wait, and end. Nested steps use the same typed shape. Local atomic transaction facts and distributed compensation remain distinct.

## 10. Root-first fixed selectors

Selectors are versioned, fixed, typed, and introspectable. They are not an arbitrary graph-query language.

Preferred selectors begin with the outer semantic scope:

```text
groups.each / groups.all
groups.schemas.each / groups.schemas.all
groups.schemas.objects.each / groups.schemas.objects.all
groups.schemas.enums.each / groups.schemas.enums.all
groups.schemas.dtos.each / groups.schemas.dtos.all
groups.operations.each / groups.operations.all
groups.operations.inputs.each / groups.operations.inputs.all
groups.operations.outputs.each / groups.operations.outputs.all
groups.operations.failures.each / groups.operations.failures.all
groups.views.each / groups.views.all
groups.storage.mappings.each / groups.storage.mappings.all
groups.workflows.each / groups.workflows.all
groups.policies.each / groups.policies.all
groups.events.each / groups.events.all
```

Inside an active group scope, parent-scoped selectors use the singular outer context first:

```text
group.schemas.each
group.operations.each
group.views.each
group.storage.mappings.each
group.workflows.each
group.policies.each
group.events.each
```

Global selectors such as `operations.each` or `schemas.all` may be supported for genuinely project-wide reports and indexes, but they are discouraged for ordinary generation. Packs should not select all operations and then reconstruct group ownership in templates.

There are no selectors such as `http.groups`, `events.operations`, `access.operations`, or arbitrary `where/traverse/depth` YAML queries. When a repeated real-world need justifies a filtered view, CodepotG adds a named fixed selector through a kernel version.

## 11. Naming contract

Every named semantic value uses one ordering:

```text
x.name.{casing}.{number}
```

Examples:

```text
field.name.camel.original
schema.name.pascal.singular
operation.name.kebab.plural
mapping.schema.name.pascal.singular
```

Short number aliases are allowed:

```text
o = original
s = singular
p = plural
```

Do not introduce reversed forms such as `name.singular.camel` or language-owned names such as `language.className`.

## 12. Templates own every emitted character

All generated text, symbols, annotations, modifiers, types, literals, imports, exports, comments, framework calls, workflow code, and validation syntax are authored in templates, macros, partials, or static files.

CodepotG provides:

- immutable semantic facts and relationships;
- stable identities and provenance;
- naming projections;
- selected contexts and related objects;
- planned artifacts and declared symbols;
- resolved provider identities and module/path facts;
- effective access/execution values;
- deterministic ordering and diagnostics.

Language adapters may detect target suffixes, validate target identifiers/filenames, calculate target-aware module-path facts, and expose documented capability/validation information. They must not render types, literals, comments, import/export statements, decorators, validators, or framework syntax.

## 13. Generated dependency contract

A pack declares generated dependencies by selection key. The planner matches consumer and provider artifacts through semantic identity, scope, and explicitly declared symbols. It resolves provider artifacts and path/module facts before rendering.

The template receives immutable descriptors and authors the syntax. For example, a template may use:

```jinja
{% for module in imports.schemaType.modules %}
import type { {{ module.symbols | join(", ") }} } from "{{ module.specifier }}";
{% endfor %}
```

The exact text above is pack-owned. CodepotG does not inject it.

## 14. Validation, planning, and impact

Before rendering, CodepotG validates the semantic model and complete generation plan, including:

- missing schema/operation/policy/event/workflow references;
- invalid storage fields and relations;
- invalid workflow transitions and compensation mappings;
- invalid access inheritance or policy uses;
- unsupported/unknown facets and selectors;
- missing or ambiguous generated providers;
- duplicate symbols and destinations;
- dependency/include/export cycles;
- path and capability violations.

Planning registers every artifact identity, destination, declared symbol, dependency, import/export relationship, and source semantic identity before emission. Invalid plans never call renderers or writers.

The same graph supports dry-run and blast-radius reporting:

```text
semantic change
→ affected semantic relations
→ affected selections
→ affected invocations
→ affected artifacts
```

Deterministic full generation is implemented first. Incremental generation may later use declared dependencies, selection scope, template/include digests, conservative context dependencies, and optional read tracing. It must fall back to safe broader regeneration when exact impact cannot be proven.

The dependency lock records inputs and behavior versions. Generated output hashes and incremental state belong to an ownership/generation-state manifest, not the dependency lock.

## 15. Kernel growth procedure

Adding a concept requires all of the following:

1. define its framework-neutral meaning;
2. decide whether it is an object, relation, facet, or value;
3. define typed immutable models and provenance;
4. define valid attachment/containment locations;
5. define source normalization rules;
6. define semantic validation and diagnostics;
7. define root-first fixed selectors where needed;
8. define immutable template-context exposure;
9. define serialization, hashing, ordering, and compatibility;
10. add realistic source and template-pack simulations;
11. update IR/behavior versions and all affected package tasks.

Adapters translate into CodepotG's known kernel. Packs consume CodepotG's known kernel. Neither may redefine it.
