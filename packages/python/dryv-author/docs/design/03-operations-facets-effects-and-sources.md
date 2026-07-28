# Operations, facets, effects, and value sources

## Operation core

Authoring compiles into:

```text
operation
├── inputs
├── outputs
├── failures
├── effects
└── known facets
```

Inputs and outputs are typed schema uses. Direction belongs to the operation use, not permanently to the schema.

## Authoring sugar

Convenience methods may exist:

```text
operation
query
command
listener
scheduled
```

Every method creates an ordinary operation. They never add query/command/listener selector roots or parallel kernel hierarchies.

## Known facets only

Builders may target only public core facets. Unknown facets are errors. Initial expected builders cover:

- HTTP;
- access;
- trigger;
- execution;
- events.

The author package does not register facets.

## HTTP neutrality

HTTP authoring connects operation uses to neutral transport facts:

- method and path;
- path/query/header/cookie/body input bindings;
- status and response bindings;
- media/header/cookie effects supported by core;
- deprecation and documentation.

It never references Express, NestJS, FastAPI, controllers, middleware classes, or runtime request/response objects.

## Effects

Effects describe consequences beyond direct outputs, using core-owned typed contracts such as events. Cross-operation cache/invalidation concepts remain design candidates only when core defines them. Tags may temporarily guide templates but may not create semantic relationships.

## Execution hooks

Execution helpers reference ordinary operations through known phases. They do not introduce arbitrary Python callables or a new executable hierarchy.

## Value sources

A value source is a proposed neutral semantic object that identifies:

- source operation;
- operation output or item collection;
- value field;
- label field(s);
- optional search/query input binding;
- optional dependent input bindings.

It is not tied to HTTP, frontend fetching, database joins, or a particular control. A source may support web selectors, mobile pickers, CLI prompts, generated tests, or documentation.

Until core publishes `ValueSource`, author compilation of value-source declarations must return a stable unsupported-core diagnostic rather than storing a private shape in extensions.
