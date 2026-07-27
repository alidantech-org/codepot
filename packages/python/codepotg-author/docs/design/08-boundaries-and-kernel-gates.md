# Boundaries and intentional kernel gates

## Locked neutrality

The authoring package represents a facade of recurring software design patterns. It remains oblivious to concrete runtime implementation details.

It does not model or bind:

```text
PostgreSQL/MongoDB-specific syntax
Prisma/TypeORM/SQLAlchemy objects
React/Flutter/Next.js/NestJS/FastAPI APIs
framework routers or state libraries
raw runtime request/response objects
SQL ASTs or database query planners
visual layout or animation systems
package-manager or deployment commands
```

Packs and templates interpret neutral facts.

## No private semantic escape

The package may not introduce:

- private IR nodes;
- private facets;
- author-only selector roots;
- arbitrary semantic metadata bags;
- target-specific bindings keyed to semantic IDs;
- template variables not published by core;
- authoring JSON as a second source of truth.

## Current public-core work

The first implementation can build typed authoring for concepts already in public core:

- contract/groups;
- structural schemas and fields;
- operations, inputs, outputs, failures;
- current known facets;
- policies/events;
- storage mappings;
- views/parts/triggers currently supported;
- workflows and compensation;
- provenance, documentation, extensions/raw within existing rules.

## Required intentional core evolution

The following approved ideas require separate core tasks before complete compilation:

1. immutable `TagSet` and safe template tag API;
2. categorized guidance/info notes;
3. typed connected field capability facets;
4. typed semantic field-reference facts when not already representable;
5. neutral value sources;
6. contract-level neutral presentations, placements, addresses, and navigation;
7. any expanded HTTP inbound/outbound binding facts absent from the public facet;
8. a public canonical IR JSON/YAML codec if core does not already expose one;
9. fixed selectors and bounded template contexts for every newly approved semantic object.

Each change requires architecture docs, typed models, validation, version changes, selectors, contexts, fixtures, and compatibility rules.

## Parallel implementation rule

The author-package implementation agent must not modify `packages/python/codepotg-v2/src/codepotg/**`. It implements the available subset and records exact blockers. A separately approved core lane may later publish the missing contracts, after which author compilation can be completed without redesigning the author API.
