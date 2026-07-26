# Template-engine adapter contract

## Responsibility

A template-engine adapter compiles and renders templates using immutable prepared contexts and a controlled pack template registry.

It owns template-language behavior only. It does not own target-language rules, source normalization, file planning, output writing, or commands.

## Installable package

A template engine is an independently versioned Python package, for example:

```text
codepotg-template-jinja
codepotg-template-mako
```

It registers a factory through `codepotg.template_engines`.

## Engine descriptor

The descriptor declares:

- engine ID and aliases;
- recognized template suffixes;
- plugin and engine behavior versions;
- supported core/IR versions;
- capabilities;
- typed engine-rule schema;
- factory;
- trust classification.

Template suffix inference uses the final known suffix, for example `.jinja`, `.jinja2`, or `.j2`.

## Required services

An engine adapter implements:

- template source compilation;
- immutable context rendering;
- controlled include and inheritance resolution;
- registered filters, functions, tests, and globals;
- undefined-value behavior;
- whitespace behavior;
- output size and recursion safeguards;
- optional named-output block support when declared;
- compilation cache scoped by engine version, template digest, and rule digest;
- structured syntax and render diagnostics with source spans.

## Typed engine rules

The engine publishes typed models for applicable fields:

```yaml
templateEngines:
  jinja:
    undefinedBehavior: error
    whitespace:
      trimBlocks: true
      leftStripBlocks: true
      keepTrailingNewline: true
    includes:
      dynamic: false
    sandbox:
      attributeAccess: restricted
      callableAccess: registeredOnly
    limits:
      maxRenderBytes: 5000000
      maxIncludeDepth: 32
```

It publishes defaults, patches, field descriptors, merge policies, restrictions, validation, and introspection.

## Context contract

The renderer receives a prepared immutable context containing only declared data for the invocation, such as:

- selected IR item or aggregate;
- project and pack public values;
- effective target rules;
- resolved bindings;
- resolved imports;
- planned exports;
- output metadata;
- approved helper services represented through narrow safe interfaces.

Rich filesystem, resolver, runtime, registry, command, cache, or application objects must not be exposed to templates.

## Include and inheritance model

Templates resolve includes through the pack's typed template registry, not arbitrary filesystem paths.

The planner must know declared includes before rendering whenever practical. Dynamic include expressions are disabled by default and require an explicit engine/host capability when ever supported.

The include resolver validates:

- source exists inside the pack;
- included descriptor has a compatible role;
- target compatibility: same target or neutral fragment;
- no include cycle;
- depth limits;
- ignored and documentation-only files cannot be included accidentally.

A TypeScript template cannot include a Dart fragment. A target-neutral text partial may be included by either.

## Named outputs

A template may declare several named outputs only when the pack manifest declares those outputs before rendering.

The engine may offer controlled output blocks such as:

```jinja
{% output "interface" %}
...
{% endoutput %}
```

It may not emit arbitrary undeclared paths.

## Sandboxing

Downloaded declarative packs are data, not trusted Python plugins. The default engine policy prohibits:

- Python imports;
- unrestricted builtins;
- arbitrary attribute traversal;
- calling unregistered objects;
- direct filesystem access;
- process execution;
- environment access;
- network access;
- runtime registry mutation.

Security-sensitive fields are host-controlled and not pack-overridable.

## Filters and helpers

Filters and helpers are registered explicitly through typed descriptors. Each declares input/output behavior, purity expectations, version, and target/engine applicability.

Language-specific rendering should normally come from prepared language services or values, not duplicate ad hoc filters in the engine package.

## Caching

Compiled-template cache keys include:

- engine implementation and behavior version;
- engine rules digest;
- template source digest;
- include dependency digests;
- registered helper/filter version digest.

Caches are runtime/session scoped or provided through a cache port. No module-level mutable template cache is allowed.

## Prohibited responsibilities

The engine adapter must not:

- infer source schemas;
- decide which templates run;
- calculate output paths;
- resolve project package managers;
- render target-language imports independently of language adapters;
- write files;
- execute before/after commands;
- inspect CLI options;
- silently discover undeclared template dependencies by scanning arbitrary source text as the only planning mechanism.

## Conformance tests

Every engine package must test:

- suffix detection;
- deterministic rendering;
- strict undefined behavior;
- immutable context behavior;
- include resolution and cycles;
- target compatibility for fragments;
- sandbox denial cases;
- filter/helper registration conflicts;
- named output declarations;
- render size and recursion limits;
- cache key invalidation;
- source-span diagnostics;
- no filesystem, environment, network, or command access from templates.
