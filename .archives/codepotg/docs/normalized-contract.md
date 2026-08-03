# Normalized Contract Architecture

CodepotG preserves its current architecture and expands it additively:

```text
OpenAPI loader
  -> inference graph
  -> language-neutral API contract
  -> deterministic template contract
  -> language adapter
  -> Jinja template pack
  -> emission engine
```

Each boundary has one responsibility.

## OpenAPI loader

The loader reads OpenAPI 3.0 or 3.1 JSON or YAML and preserves the complete source document. It validates the minimum document shape but does not perform language-specific interpretation.

## Inference graph

Inference discovers and links:

```text
resources
schemas
operations
parameters
request bodies
responses
media types
dependencies
x-codegen definitions
frontends
entities
```

Inference may classify source information, but it does not emit target-language strings.

## Language-neutral API contract

The API contract contains stable facts that every language can consume:

```text
document information
servers and security
resources
schemas and constraints
operations and HTTP data
entities and storage behavior
access policies
cache policies
runtime hooks
frontends
dependencies
diagnostics
extensions
raw source
```

It must not contain TypeScript, Dart, Go, Rust, Java, or any other language syntax.

## Template contract

The template contract adds deterministic authoring conveniences:

```text
name variants
classified collections
contextual item views
resolved dependencies
planned imports
output path information
documentation views
language helper views
```

Templates consume this stable contract rather than loose dictionaries.

## Language adapter

The adapter translates language-neutral facts into target-language helpers:

```text
type names
literal syntax
validation syntax
safe identifiers
reserved-word handling
imports
comments
files
packages
framework conventions
post-generation tools
```

Adapters do not modify inference or discard source facts.

## Emission engine

The emission engine selects contexts, expands paths, plans dependencies and imports, enforces managed and immutable write policies, renders Jinja, and writes files.

It remains unaware of OpenAPI parsing and concrete language implementations.

## Normalized object pattern

Major contract objects follow one shape:

```text
identity
name
normalized domain facts
resolved relationships
derived convenience views
documentation and notes
extensions
raw
diagnostics where relevant
```

## Collection pattern

Collections expose:

```text
all
count
by_id
by_name
classified views
```

Ordered tuples remain authoritative for deterministic output. Lookup views provide direct access.

## Reference pattern

References expose:

```text
ref
kind
name
owner
is_resolved
target
```

The original ref and resolved target coexist. Circular references do not recursively expand the entire graph.

## Value pattern

Presence-aware values expose:

```text
value
is_set
origin
```

Origins distinguish authored, inferred, derived, and effective values.

## Information-note pattern

Structured notes use stable categories:

```text
explain
access
implement
validation
security
observability
ux
performance
testing
other
```

Unknown categories remain under `other` without data loss.

## Extension pattern

Known extension values become named properties. Unknown extension keys remain under `extensions`. The complete source object remains under `raw`.

## Diagnostics pattern

Diagnostics identify:

```text
unresolved references
malformed source values
unsupported but preserved values
raw-only values
deprecated compatibility paths
actual loss
```

The normalized contract is complete only when actual loss is zero.

## Template simplicity target

A template should be able to render a resource, operation, schema, or entity using direct properties and ordered collections. It should not need to:

```text
search the root document
parse JSON Pointer strings
merge path and operation parameters
merge inherited entity fields
infer query operators
resolve cache invalidation names
resolve access policies
resolve runtime hooks
classify response status codes
interpret x-codegen dictionaries
```

All of those operations belong before Jinja rendering.
