# Contract-provider, pack-provider, and ecosystem plugin contracts

## Contract providers

A contract provider supplies one public immutable `dryv.ir.Contract` to the runtime.

Initial provider forms:

- canonical IR JSON/YAML file;
- configured Python module callable;
- host-supplied in-memory contract.

A provider owns only the work required to obtain its contract and describe its provenance. It may contribute:

- a typed provider configuration schema;
- controlled loading or importing;
- deterministic provider identity and digest facts;
- source-aware diagnostics;
- cancellation and resource limits.

A provider does not own packs, templates, target languages, output paths, writing, commands, CLI behavior, or semantic-kernel evolution.

A provider cannot:

- add semantic node kinds, relations, schema kinds, facets, or attachment locations;
- register selectors, expression roots, template-context properties, or kernel validators;
- expose arbitrary graph or fact bags as a substitute for public Dryv contracts;
- leak parser, builder, Pydantic, module-loader, or resolver objects into planning or templates;
- return a contract that bypasses core validation.

Required conformance tests:

- deterministic immutable contract output;
- precise diagnostics and provenance;
- cancellation and bounded loading;
- no process-global mutable state;
- no provider-specific values escaping into public runtime plans or render contexts;
- stable identity/digest behavior where the provider publishes a digest;
- repeated calls do not leak session state.

The built-in `ir` provider strictly decodes canonical Dryv transport. The planned Python provider imports one explicitly configured callable and requires it to return a public `Contract`.

## Pack providers

A pack provider resolves a pack locator to an immutable local snapshot.

Planned provider forms:

- local directory;
- generic Git;
- installed Python pack distribution where supported.

A resolved pack includes:

- source identity;
- requested reference;
- immutable resolved commit or version;
- subdirectory;
- manifest path;
- content digest;
- trust metadata;
- local snapshot root.

The provider does not decode `DryvPack.yaml`, semantic contracts, or templates. It supplies the snapshot to the typed runtime pack loader.

Git providers use existing Git authentication and credential helpers. Credentials are never stored in `dryv.yaml`, `dryv.lock.yaml`, ownership state, or diagnostics.

Required provider tests:

- local path containment;
- controlled public/private Git URL handling;
- immutable commit resolution;
- subdirectory validation;
- cache integrity and reuse;
- content digest changes;
- cancellation and partial-fetch cleanup;
- no credential logging.

## Ecosystem adapters

An ecosystem adapter understands known project manifests, package-manager or toolchain capabilities, and typed project contribution/setup actions for one ecosystem.

Examples:

- Node: `package.json`, workspaces, package managers, scripts, dependencies, and exports;
- Dart: `pubspec.yaml`, SDK constraints, dependencies, assets, and workspace registration;
- future Python, Cargo, Gradle, and Maven adapters.

It may own:

- typed contribution schemas;
- manifest detection and decoding;
- owned versus contributed updates;
- toolchain and package-manager capability metadata;
- deterministic contribution planning;
- typed action resolution;
- conflict diagnostics.

It does not execute commands directly. It produces plans consumed through the approved command executor and security policy.

It cannot add semantic objects, facets, selectors, or generated application syntax. Package-manager arguments remain exact project/pack-authored values unless a separately approved typed contribution contract owns the modification.

Required ecosystem tests:

- manifest round trips;
- minimal-diff contributions where practical;
- conflict handling;
- toolchain detection precedence;
- capability intersection;
- no silent toolchain switching;
- owned versus contributed manifests;
- action resolution and lifecycle policy;
- no semantic-kernel or target-syntax ownership.

## Port boundaries

All plugin categories use public immutable request/result types. They must not import CLI modules, archived generator modules, private semantic builders, or concrete runtime singletons.
