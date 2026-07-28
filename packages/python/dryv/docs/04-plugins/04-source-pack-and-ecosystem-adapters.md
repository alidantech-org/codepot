# Source, pack-provider, and ecosystem adapter contracts

## Source adapters

A source adapter converts one declared semantic input into the closed Dryv kernel.

It owns:

- source option schema;
- source loading through controlled ports;
- syntax parsing and source-format validation;
- source-format reference resolution;
- deterministic mapping into known groups, schemas, operations, views, storage mappings, policies, events, workflows, relationships, and known facets;
- provenance and source diagnostics;
- source digest contribution.

It does not own templates, target languages, output paths, writing, commands, CLI behavior, or semantic-kernel evolution.

A source adapter cannot:

- add semantic node kinds, relations, schema kinds, or roles;
- add facets or attachment locations;
- add selectors, expression roots, template-context properties, or kernel validators;
- expose generic graph/fact bags as a substitute for typed kernel contracts;
- leak parser/library/resolver objects into core or templates;
- silently interpret unknown source metadata as supported application semantics.

Unknown source metadata may be preserved only through documented bounded immutable `extensions`, `raw`, and provenance escape hatches. Preservation does not make the metadata a supported facet or semantic object.

The OpenAPI adapter must parse once, resolve references once, decode supported OpenAPI and typed/versioned Codepot `x-codegen` metadata, and produce the canonical kernel directly. It must not expose OpenAPI-specific objects to packs/templates except through approved provenance/raw/extension values.

Required source-adapter conformance tests:

- deterministic immutable kernel output and digest;
- source-span diagnostics;
- bounded controlled reference resolution;
- cancellation;
- no mutable global parser state;
- no source-specific types escaping into public domain APIs;
- no semantic/facet/selector/context registration;
- bounded extension/raw behavior;
- source digest stability;
- in-memory and filesystem source loading.

## Pack providers

A pack provider resolves a pack locator to an immutable local pack snapshot.

Initial providers:

- local directory;
- generic Git;
- installed Python pack distribution where supported.

A resolved pack includes:

- source identity;
- requested reference;
- immutable resolved commit/version;
- subdirectory;
- manifest path;
- content digest;
- trust metadata;
- local snapshot root.

The provider does not parse `DryvPack.yaml`, semantic sources, or templates. It supplies the snapshot to the typed pack loader.

Git providers use the user's existing Git authentication and credential helpers. Tokens are never stored in `dryv.yaml` or `dryv.lock.yaml`.

Required provider tests:

- local path containment;
- public and private Git URL handling through mocked/controlled Git operations;
- immutable commit resolution;
- subdirectory validation;
- cache reuse;
- content digest changes;
- cancellation and partial fetch cleanup;
- no credential logging.

## Ecosystem adapters

An ecosystem adapter understands known project manifests, package-manager/toolchain capabilities, and typed project contribution/setup actions for one ecosystem.

Examples:

- Node: package.json, workspaces, npm/pnpm/Yarn, scripts, dependencies, exports;
- Dart: pubspec.yaml, Dart/Flutter SDK constraints, pub dependencies, assets, workspace registration;
- future Python, Cargo, Gradle, and Maven project adapters.

It may own:

- typed project contribution schemas;
- manifest detection and decoding;
- owned versus contributed manifest updates;
- toolchain/package-manager capability metadata;
- deterministic contribution planning;
- typed action resolution;
- conflict diagnostics.

It does not execute commands directly; it produces command/action plans consumed through the executor and security policy.

It also cannot add application semantic objects/facets/selectors or author generated application syntax. Package-manager command arguments remain exact project/pack-authored commands unless a separately approved project-contribution contract explicitly owns a typed change.

Required ecosystem tests:

- manifest round trips;
- minimal-diff contribution behavior where practical;
- conflict handling;
- package-manager/toolchain detection precedence;
- capability intersection;
- no silent toolchain switching;
- owned versus contributed manifests;
- action resolution and command capability declarations;
- lifecycle-script policy;
- no semantic-kernel or generated-syntax ownership.

## Port boundaries

All adapter categories use public immutable request/result types. They must not import CLI modules, old generator modules, private semantic builders, or concrete runtime singletons.
