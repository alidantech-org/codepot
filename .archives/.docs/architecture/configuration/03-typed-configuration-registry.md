# Typed configuration registry

## Goal

Dryv must understand configuration through typed models and registered decoders. Raw YAML mappings must never flow into application, domain, adapter, or template logic.

## Processing pipeline

```text
YAML or JSON bytes
        ↓
location-aware syntax document
        ↓
(apiVersion, kind) schema resolution
        ↓
typed structural decoding
        ↓
semantic validation
        ↓
plugin-owned option and rule decoding
        ↓
canonical immutable configuration
        ↓
resolved project and pack plan
```

## Document layer

The infrastructure parser produces typed syntax nodes:

- mapping node;
- sequence node;
- scalar node;
- null node;
- source span;
- document path;
- original key text.

Duplicate YAML keys are errors. YAML aliases and tags must be handled through an explicit safe policy rather than exposed as arbitrary Python objects.

## Registry key

The configuration registry resolves exact pairs:

```text
(Project, dryv.dev/v1)
(TemplatePack, dryv.dev/v1)
(LockFile, dryv.dev/v1)
```

Unsupported versions fail with a diagnostic listing supported versions. V2 does not guess or fall back to old `tasks` or `paths.yaml` formats.

## Decoder contract

A decoder:

- accepts syntax nodes, not dictionaries;
- validates required and allowed fields;
- preserves source spans on typed values or provenance records;
- produces immutable typed models;
- reports all practical structural diagnostics in one pass;
- never resolves plugins, reads files, executes commands, or performs generation.

## Structural versus semantic validation

Structural validation covers:

- field presence;
- field types;
- enum values;
- duplicate IDs inside one document;
- basic scalar constraints;
- unknown fields.

Semantic validation covers:

- source references;
- pack references;
- option and binding compatibility;
- toolchain constraint intersection;
- target/engine availability;
- output collisions;
- dependency cycles;
- security and override permissions;
- command approvals;
- lock drift.

## Plugin-owned schemas

Plugins register typed schema providers for their owned sections.

Examples:

```text
sources.<id>.options                 → source adapter
languages.typescript                → TypeScript language adapter
languages.dart                      → Dart language adapter
templateEngines.jinja               → Jinja engine adapter
dependencies.node                   → Node ecosystem adapter
packs.<instance>.options            → selected pack
packs.<instance>.bindings.<binding> → selected pack + target adapter
```

The core registry owns dispatch and standard metadata. Plugins own the typed model and validation for their fields.

## Rule descriptors

Every configurable field must be introspectable through a descriptor containing:

- canonical path;
- owner plugin and API version;
- value type;
- default;
- required state;
- merge policy;
- override permissions;
- security classification;
- description;
- examples;
- introduced version;
- deprecation metadata when applicable.

This metadata powers:

- YAML schema generation;
- `dryv configure`;
- CLI and MCP inspection;
- editor completion;
- documentation generation;
- pack validation;
- project override validation.

## Unknown fields

Unknown fields are errors by default. Extension data is allowed only beneath explicit namespaced extension points whose decoders are registered.

Silently ignoring fields is prohibited because misspellings can change generated code.

## Serialization

Canonical serializers must:

- produce stable field ordering;
- preserve user-controlled comments only when the chosen YAML editing library can do so safely;
- write only documented public fields;
- never serialize secrets;
- support update-in-place for `dryv configure` without rewriting unrelated pack entries where practical.

## No compatibility decoder

The v2 registry intentionally has no decoder for:

- unversioned v1 project configuration;
- root `tasks`;
- project-level `language`;
- `templateDir`;
- `paths.yaml`.

The old package remains available to run those contracts. Re-authoring guides and tools may explain or assist conversion, but the v2 runtime does not contain old execution semantics.

## Tests

Required tests include:

- exact registry dispatch;
- unsupported kind/version diagnostics;
- unknown field diagnostics with spans;
- duplicate key rejection;
- plugin schema registration conflicts;
- immutable output models;
- stable schema introspection;
- no dictionary leakage below configuration boundaries.
