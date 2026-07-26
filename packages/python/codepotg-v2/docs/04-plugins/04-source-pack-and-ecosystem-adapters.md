# Source, pack-provider, and ecosystem adapter contracts

## Source adapters

A source adapter converts one declared semantic input into the neutral IR.

It owns:

- source option schema;
- source loading through controlled ports;
- syntax parsing;
- source validation;
- reference resolution;
- direct normalization to neutral IR;
- provenance and source diagnostics;
- source digest contribution.

It does not own templates, target languages, output paths, writing, commands, or CLI behavior.

The initial OpenAPI adapter must parse once, resolve references once, and produce the canonical IR directly. It must not expose OpenAPI-specific objects to language adapters or templates except through explicitly typed provenance/extensions approved by the IR contract.

Required source-adapter conformance tests:

- deterministic IR;
- source-span diagnostics;
- bounded reference resolution;
- cancellation;
- no mutable global parser state;
- no source-specific types escaping into core domain APIs;
- source digest stability;
- in-memory and filesystem source loading.

## Pack providers

A pack provider resolves a pack locator to an immutable local pack snapshot.

Initial providers:

- local directory;
- generic Git;
- GitHub shorthand resolved through Git;
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

The provider does not parse `CodepotgPack.yaml`; it supplies the snapshot to the typed pack loader.

Git providers use the user's existing Git authentication and credential helpers. Tokens are never stored in `codepotg.yaml` or `codepotg.lock`.

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

An ecosystem adapter understands project manifests, dependency intent, package-manager capabilities, and typed setup actions for one ecosystem.

Examples:

- Node: package.json, workspaces, npm/pnpm/Yarn, scripts, dependencies, exports;
- Dart: pubspec.yaml, Dart/Flutter SDK constraints, pub dependencies, assets, workspace registration;
- future Python, Cargo, Gradle, and Maven adapters.

It owns:

- typed dependency schema;
- manifest detection and decoding;
- owned versus contributed manifest updates;
- toolchain/package-manager capability metadata;
- deterministic contribution planning;
- typed action resolution;
- conflict diagnostics.

It does not execute commands directly; it produces command/action plans consumed through the command executor and security policy.

Required ecosystem tests:

- manifest round trips;
- minimal-diff contribution behavior where practical;
- dependency conflict handling;
- package-manager detection precedence;
- capability intersection;
- no silent toolchain switching;
- owned versus contributed manifests;
- action resolution and command capability declarations;
- lifecycle-script policy.

## Port boundaries

All three adapter categories use public immutable request/result types. They must not import CLI modules, old generator modules, or concrete runtime singletons.
