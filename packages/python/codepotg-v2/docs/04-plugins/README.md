# 04 — Installable plugin packages

CodepotG extensions are ordinary installable, versioned, deployable Python packages discovered through Python entry points. Official and third-party plugins use the same public contracts and receive no hidden access to core internals.

## Planned package families

```text
codepotg-openapi
codepotg-language-typescript
codepotg-language-dart
codepotg-template-jinja
codepotg-pack-typescript-sdk
codepotg-pack-dart-sdk
codepotg-pack-flutter-sdk
```

Each package has its own README, task ledger, tests, and progress record under `packages/python`.

## Source adapters

A source adapter loads one source format and normalizes directly into the neutral IR. It does not plan templates, render code, write files, run commands, or expose source-specific graphs to language adapters and templates. The initial adapter is OpenAPI.

## Language adapters

A language adapter is resolved per template from its target extension or explicit target. It owns target syntax only: identifiers, reserved words, types, literals, comments, imports, exports, module paths, package paths, and typed language-rule decoding and merging.

It does not load OpenAPI, select templates, choose output paths, own template engines, write files, run commands, or assume a framework. TypeScript does not mean NestJS, Next.js, React, or Node. Dart does not mean Flutter.

Internally, target descriptors distinguish programming languages, markup, data, configuration, query languages, and plain text while preserving the simple user-facing `languages` section.

## Template-engine adapters

A template-engine adapter renders an immutable plain context and resolves includes only through the pack template registry. It publishes a typed, locked engine configuration model. Security-sensitive settings such as arbitrary Python access, unrestricted filesystem access, or dynamic imports are host-controlled and cannot be enabled by a downloaded pack.

The initial engine is sandboxed Jinja.

## Plugin metadata and compatibility

Every plugin publishes an ID, aliases, package version, plugin API version, supported IR and configuration versions, capabilities, entry-point factory, typed option or rule contract, and diagnostics metadata. Core distinguishes package release version, Python public API version, plugin API version, IR version, project schema version, pack schema version, and lock-file version.

Instance registries validate duplicate IDs, aliases, API compatibility, capabilities, and conflicts. Import-time decorator registries and directory scanning of internal packages are forbidden.

## Conformance testing

Core publishes reusable contract suites. Every implementation proves deterministic behavior, immutable inputs, stable diagnostics, capability declarations, option decoding, rule merging, and absence of hidden global state. Removing an official adapter package must only make that capability unavailable; it must not break core imports.
