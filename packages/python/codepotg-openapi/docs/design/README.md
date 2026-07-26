# OpenAPI source adapter design reference

## Role

This package loads OpenAPI YAML/JSON, validates and resolves references once, decodes supported typed/versioned Codepot `x-codegen` metadata, and normalizes directly into the closed CodepotG semantic kernel.

It does not select target languages, templates, packs, outputs, commands, files, selectors, or generated architecture.

## Planned plugin entry point

```toml
[project.entry-points."codepotg.source_adapters"]
openapi = "codepotg_openapi.plugin:create_plugin"
```

## Project configuration example

```yaml
sources:
  backendApi:
    adapter: openapi
    path: ./openapi.yaml
    options:
      validation: strict
      externalReferences: localOnly
      maxReferenceDepth: 64
      xCodegenPolicy: strict
```

All options are typed and target-neutral. They cannot choose frameworks, output syntax, selectors, or new facets.

## Processing

```text
controlled source loader
        ↓
safe YAML/JSON parse with spans
        ↓
OpenAPI structural validation
        ↓
canonical reference resolution
        ↓
typed/versioned x-codegen decode
        ↓
closed-kernel normalization
        ↓
core semantic validation
        ↓
immutable source result + digest
```

No compatibility graph, generic fact bag, or duplicate target-specific model is produced.

## Standard OpenAPI mapping

### Groups

OpenAPI has no universal application-group concept. The adapter applies one explicit behavior-versioned grouping policy, for example operation tags with deterministic fallback groups. It produces `contract.groups`; it does not produce neutral resources, services, modules, or features.

An operation assigned to several tags must follow a documented deterministic policy rather than being duplicated silently.

### Schemas

OpenAPI schemas normalize into structural kernel schemas:

```text
primitive
literal
enum
object
array
map
tuple when representable
union/intersection/composition when semantically valid
alias/reference
unknown/unsupported with diagnostics
```

`model`, `entity`, request, response, class, interface, type, struct, and record are not schema kinds.

Required/optional, nullable, read-only/write-only, formats, defaults, examples, and constraints normalize into known field/schema facts. Input/output direction remains on operation schema-use relationships.

### Operations

Path operations normalize into:

```text
operation.inputs
operation.outputs
operation.failures
operation.effects
operation.facets
```

Parameters and request bodies become neutral inputs. Successful responses become outputs. Declared error responses become failures. HTTP-only placement and response details live under `operation.facets.http`.

### HTTP facet

The HTTP facet contains known facts such as:

```text
method
path
path/query/header/cookie bindings
request body/media types
response status/media/header bindings
deprecation
```

Templates decide whether these facts become NestJS decorators, Express routing, Spring annotations, client requests, tests, or documentation.

### Access

OpenAPI security schemes and requirements normalize into known policies/access facets where semantics are representable:

```text
group.policies
operation.facets.access.declared
operation.facets.access.effective
```

The adapter preserves OpenAPI any-of/all-of security requirement structure and scopes. It does not invent full RBAC/permission/ownership semantics that the source does not provide.

## Typed `x-codegen` mapping

The `x-codegen` extension is not an untyped escape hatch. Supported versions have typed decoders, source-spanned validation, compatibility rules, and deterministic mapping into known kernel contracts.

Approved categories may map as follows:

```text
x-codegen stable IDs           → semantic identities
x-codegen grouping             → contract/groups ownership
x-codegen schema roles         → controlled schema roles such as dto
x-codegen operation metadata   → known operation fields/facets/effects
x-codegen storage              → group.storage.mappings
x-codegen views/interactions   → group.views, parts, triggers, flows
x-codegen policies/access      → group.policies and access facets
x-codegen events               → group.events and event effects/facets
x-codegen listeners            → operations with trigger facets
x-codegen execution hooks      → operation execution facets
x-codegen workflows            → group.workflows, steps, transitions
x-codegen compensation         → step.compensation
```

The adapter may not turn an unknown extension key into a new kernel object or facet. Unsupported metadata is diagnosed or preserved through bounded raw/extensions according to explicit policy.

## Events and listeners

A declared event becomes `group.events`. An operation that causes it references it under `operation.effects.events`. Publication/consumption/channel facts use the known events facet. An event listener is an ordinary operation with `operation.facets.trigger.event`.

The adapter must distinguish occurrence, message payload, delivery channel, and consumer/producer binding rather than collapsing them into one opaque source object.

## Workflows and compensation

Typed `x-codegen` workflow metadata may normalize into first-class workflows with:

```text
inputs
outputs
steps
transitions
failures
effects
known facets
```

An operation step references one forward operation and may optionally contain one compensation operation plus typed mappings/retry/timeout/failure policy. Compensation is corrective work, not an assumed exact inverse.

The adapter validates references and source shape. Core owns final kernel semantic validation. Neither layer generates Temporal, Step Functions, saga, queue, or application-service syntax.

## Views and storage

View metadata normalizes only when it represents known view/part/trigger/flow semantics. It does not create neutral frontend/UI/page/screen/component/widget object kinds.

Storage metadata normalizes into storage mappings linked to schemas. It does not create a neutral entity/model object. ORM entity classes, repositories, migrations, and SQL are template outputs.

## Provenance and bounded preservation

Every normalized item records canonical source identity and source spans where available.

The adapter may preserve approved OpenAPI or `x-codegen` metadata in bounded immutable values when it is not part of the known kernel. It may not expose:

- parser nodes;
- mutable mappings;
- resolver instances;
- OpenAPI library classes;
- executable callables;
- arbitrary filesystem/network handles.

## Determinism and digest

The source/behavior digest includes:

- canonical document contents and resolved references;
- adapter version and behavior version;
- OpenAPI support version;
- `x-codegen` schema/behavior version;
- all normalization/grouping/operation-ID policies;
- controlled external-reference behavior;
- diagnostics policy that affects accepted output.

## Boundaries

- Source adapters translate into CodepotG's known kernel and cannot extend it.
- External references require host-authorized loaders.
- OpenAPI-specific types never escape into core consumers.
- Target syntax, generated paths, symbols, imports, templates, and commands are outside this package.

See `../tasks/00-package-plan.md` and the core source-adapter/closed-kernel contracts.
