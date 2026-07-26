# Package architecture

## Goal

CodepotG v2 is a clean, importable Python application with explicit domain boundaries and independently installable plugins.

The implementation directory is `packages/python/codepotg-v2`, but the eventual supported Python namespace is `codepotg`.

## Core source layout

```text
src/codepotg/
├── __init__.py
├── api/
├── application/
├── config/
├── domain/
│   ├── ir/
│   └── generation/
├── plugins/
├── ports/
├── runtime/
├── infrastructure/
└── cli/
```

## Responsibilities

### `api`

Stable Python-facing requests, results, events, sessions, application facade, and supported exports.

It contains no filesystem, CLI, OpenAPI, Jinja, TypeScript, Dart, or package-manager implementation.

### `application`

Use cases and orchestration:

- configure;
- validate;
- inspect;
- compile plan;
- generate;
- resolve packs;
- manage approvals;
- inspect plugins;
- inspect readiness.

Application services depend on domain types and ports, not concrete infrastructure.

### `config`

Typed configuration infrastructure:

- location-aware document nodes;
- schema registry;
- project and pack models;
- typed decoding;
- semantic validation;
- rule descriptors and patches;
- schema introspection and serialization.

Raw YAML and JSON values stop here.

### `domain.ir`

Source-neutral semantic representation:

- documents and provenance;
- names;
- schemas and fields;
- type expressions;
- enums;
- operations;
- parameters;
- requests and responses;
- entities and relationships;
- diagnostics attached to source locations.

It must not import OpenAPI, template engines, languages, filesystems, commands, caches, or CLI concerns.

### `domain.generation`

Generation semantics:

- pack and file descriptors;
- selections;
- template invocations;
- artifacts and outputs;
- bindings and resolved imports;
- dependency and provider graphs;
- command plans;
- readiness status;
- lifecycle and ownership policies.

### `plugins`

Public plugin descriptors, API versions, capabilities, entry-point discovery, instance registries, and compatibility validation.

Official plugins use the same APIs as third-party plugins.

### `ports`

Interfaces implemented by plugins or infrastructure:

- source adapter;
- language adapter;
- template-engine adapter;
- pack provider;
- ecosystem/toolchain adapter;
- artifact writer;
- cache store;
- command executor;
- approval store;
- event sink.

### `runtime`

Immutable runtime composition and isolated generation sessions. It coordinates concrete services selected by the host application without exposing process-global state.

### `infrastructure`

Concrete implementations for:

- YAML/JSON parsing;
- local and Git pack loading;
- filesystem and memory writers;
- content-addressed cache;
- subprocess execution;
- lock files;
- approval persistence;
- Python entry-point discovery.

### `cli`

Thin argument parsing and terminal presentation only. It constructs typed application requests, invokes the Python API, renders results, and selects exit codes.

## Dependency direction

```text
CLI / Python facade / MCP / HTTP
                │
                ▼
          application
           │        │
           ▼        ▼
        domain     ports
                     ▲
                     │
              infrastructure
```

Rules:

- domain imports no application, infrastructure, runtime, or CLI module;
- application imports domain and ports, not concrete infrastructure;
- infrastructure implements ports and may import domain/config contracts;
- CLI imports only public API and terminal formatting helpers;
- plugin packages import only published public contracts;
- adapters never import another adapter's internals.

## Distribution topology

The planned published distributions are:

```text
codepotg-core
codepotg
codepotg-openapi
codepotg-language-typescript
codepotg-language-dart
codepotg-template-jinja
codepotg-pack-typescript-sdk
codepotg-pack-dart-sdk
codepotg-pack-flutter-sdk
```

`codepotg-core` is minimal. `codepotg` is the batteries-included user distribution that installs compatible official defaults.

## Namespace transition rule

The v2 package is developed separately from the old package and is tested in an isolated environment. It must not depend on side-by-side installation of two distributions that both own the `codepotg` namespace.

The release cutover replaces the old distribution rather than merging the implementations.

## Architecture tests

The core test suite must verify:

- import direction;
- public versus private namespaces;
- no old package imports;
- no CLI dependency below CLI;
- no plugin-specific imports in core;
- no process-global registry mutation;
- package installation and import in an isolated environment.
