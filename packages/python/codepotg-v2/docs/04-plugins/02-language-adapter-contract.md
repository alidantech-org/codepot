# Language and target-syntax adapter contract

## Responsibility

A language adapter implements the semantics and configurable conventions of one target syntax. It is resolved independently for every template file from the template's detected or explicit target.

A project and pack may use many language adapters in one generation run.

## Installable package

A language adapter is an ordinary independently versioned Python distribution:

```text
codepotg-language-typescript
codepotg-language-dart
codepotg-language-python
```

It registers a factory through `codepotg.language_adapters`.

## Target descriptor

The adapter declares one or more target descriptors:

```text
id
aliases
file extensions
syntax category
capabilities
rule schema
behavior version
```

Syntax categories may include programming language, markup, data, configuration, query language, and plain text.

Extension resolution uses longest-known matching. For example, `.tsx` resolves before a generic `.x` registration. Removing the engine suffix never changes the intended output suffix.

## Required semantic services

An adapter implements applicable services for:

- identifier validation and escaping;
- naming transforms by semantic role;
- file naming and extension conventions;
- primitive and composite type rendering;
- optional versus nullable behavior;
- generics, unions, intersections, functions, records, arrays, maps, and language-supported constructs;
- enum representation;
- literal rendering and escaping;
- comments and documentation comments;
- import request resolution and rendering;
- export rendering;
- module/package path calculation;
- relative path calculation;
- alias and barrel behavior;
- import deduplication and collision aliasing;
- stable sorting and grouping;
- language capability reporting.

The adapter may internally split these into focused policies and renderers.

## Standard rule families

Every adapter publishes typed models for applicable sections:

```yaml
languages:
  typescript:
    identifiers: {}
    naming: {}
    files: {}
    modules: {}
    imports: {}
    exports: {}
    types: {}
    literals: {}
    comments: {}
    documentation: {}
    formatting: {}
```

The adapter publishes:

- full default rules;
- pack-rule decoder;
- override-patch decoder;
- field descriptors;
- merge policies;
- hard override restrictions;
- final semantic validation;
- schema/documentation introspection.

## Import contract

Templates request semantic imports rather than calculating strings.

A request identifies:

- logical symbol;
- symbol kind;
- provider artifact or project binding;
- import style preference;
- type-only/value usage where meaningful;
- current output artifact.

The adapter resolves module paths using effective rules and produces import descriptors or rendered statements for the template context.

It must support project bindings such as module strings, real project paths, package paths, namespaces, default barrels, binding groups, and raw escape hatches where declared.

## Effective rules

The adapter receives ordered typed rule layers from core and applies only core-defined merge operations. It returns an immutable final rule object and diagnostics.

The adapter cannot read `codepotg.yaml` or `CodepotgPack.yaml` directly.

## Capabilities

Capabilities are precise feature identifiers, for example:

```text
type.optional
type.nullable
type.union
type.intersection
type.generic
import.named
import.default
import.namespace
import.alias
import.type_only
export.named
enum.string
comment.documentation
module.package_path
```

Templates or packs may require capabilities. Missing capabilities are reported before rendering.

## Context safety

The adapter receives immutable IR and generation descriptors. It must not mutate source IR, template selections, or artifact plans.

## Prohibited responsibilities

A language adapter must not:

- parse OpenAPI or other source files;
- select records or templates;
- discover packs;
- render Jinja or another engine;
- write output files;
- execute commands;
- own cache persistence;
- inspect CLI arguments;
- encode framework architecture that belongs to a pack;
- assume TypeScript means Node/NestJS/Next.js or Dart means Flutter.

## Factory example

```python
def create_plugin() -> LanguageAdapterPlugin:
    return LanguageAdapterPlugin(
        id="typescript",
        version="1.0.0",
        api_version="1",
        ir_versions=">=2,<3",
        targets=(typescript_descriptor,),
        rules=typescript_rule_schema,
        factory=TypeScriptLanguageAdapter,
    )
```

## Conformance tests

Every language package must run tests for:

- deterministic output;
- identifier roles and reserved words;
- every declared primitive and composite type capability;
- nullable and optional distinctions;
- literal escaping;
- module and project-path imports;
- barrel deduplication;
- import alias conflicts;
- relative path calculation;
- rule decoding, merge, restrictions, and introspection;
- no IR mutation;
- thread/session isolation;
- extension inference;
- plugin descriptor compatibility.

Language-specific packages add focused tests for their own syntax.
