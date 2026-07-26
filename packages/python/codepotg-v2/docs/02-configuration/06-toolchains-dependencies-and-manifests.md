# Toolchains, dependencies, and project manifests

## Goal

CodepotG must integrate with real Node, Dart, Flutter, and future project ecosystems without turning the semantic kernel or pack manifest into a package-manager abstraction language.

The approved baseline is deliberately narrow:

- packs author complete manifests they own as ordinary templates;
- packs author exact optional commands with opaque argument arrays;
- project/host configuration supplies executable names/paths and approval policy;
- ecosystem adapters may later inspect or plan typed changes to existing user-owned manifests through separately approved contracts;
- no pack-level `dependencies`, `integration`, traits, setup profiles, or automatic package-manager conversion exists in the baseline `CodepotgPack.yaml`.

## Owned manifests

When a pack creates a complete standalone product, it authors its manifest directly:

```text
templates/package.json.jinja
templates/pubspec.yaml.jinja
templates/pyproject.toml.jinja
```

The template owns every manifest field and dependency declaration. Options/bindings may provide typed values such as package name or version, but core does not understand or rewrite the generated manifest.

The output is planned, rendered, validated, staged, and owned like every other artifact.

## Existing project manifests

A pack must not replace an existing user-owned `package.json`, `pubspec.yaml`, or other manifest unless the project explicitly designates that output as pack-owned.

Integration with an existing manifest requires a known ecosystem-adapter contract that is:

- typed and versioned;
- separately approved and documented;
- explicit in the project plan;
- limited to known manifest operations;
- conflict-detecting and source-preserving where practical;
- subject to host/project permissions.

This is infrastructure/project integration, not application semantic-kernel extension.

Until such a contract is implemented for a specific ecosystem, the pack provides:

- exact optional commands;
- documented manual actions;
- required bindings;
- readiness warnings.

It does not add arbitrary manifest contribution dictionaries to `CodepotgPack.yaml`.

## Exact commands

Dependency installation and project tools are represented as exact authored commands:

```yaml
executables:
  packageManager: pnpm

commands:
  after:
    installRuntime:
      executable: packageManager
      arguments: [add, axios@^1.0.0]

    typecheck:
      executable: packageManager
      arguments: [exec, tsc, --noEmit]
      optional: true
```

Core treats arguments as opaque tokens. It does not:

- translate a dependency map into npm/pnpm/Yarn/Dart commands;
- select versions;
- infer runtime versus development dependencies;
- rewrite package-manager syntax;
- silently switch package managers;
- execute without policy/approval.

A project may replace the executable name/path while preserving the exact pack-authored argument list unless it explicitly overrides/disables the command through typed project configuration.

## Toolchain/executable facts

The project may declare executable names/paths and host capabilities required to resolve commands:

```yaml
executables:
  packageManager: pnpm
  dart: dart
  flutter: flutter
```

A separately approved ecosystem adapter may inspect known project metadata and offer candidates, but ambiguous discovery is never selected silently.

Toolchain versions/capabilities may be reported by inspection or setup actions. They do not alter the closed application semantic kernel or generated template context unless a documented binding/option explicitly supplies a value.

## Pack product boundary

One `CodepotgPack.yaml` represents one coherent product and deterministic file inventory.

Do not add pack traits/profile matrices such as:

```text
createsProject
ownsFolder
contributesFiles
runnableAlone
manifestMode
standalonePackage
contribute
minimal
monolithic
```

A materially different standalone package, existing-project integration, framework architecture, or monolithic artifact is a separate pack with its own identity, manifest, templates, tests, and versioning.

This keeps pack behavior inspectable from the filesystem and selection registry.

## Ecosystem adapter boundary

An ecosystem adapter may eventually own known operations such as:

```text
inspect existing package manifest
validate package/workspace identity
plan a typed dependency addition
plan a typed asset/workspace/export contribution
report conflicts/manual steps
```

It cannot:

- add semantic objects, facets, selectors, or template-context values;
- render application source code;
- turn arbitrary pack dictionaries into manifest mutations;
- execute commands directly;
- bypass command approval or writer ownership;
- infer package changes from application IR without an explicit pack/project request.

Every contribution is visible in the complete plan before modification.

## Security

Installation can run third-party lifecycle scripts and access networks. Exact commands declare requested capabilities and remain subject to the strictest host/project policy.

Downloaded pack commands require approval by default. Approval identity includes exact pack source/commit/digest, executable reference, argument list, working directory, environment/capability request, and relevant lock identity.

## Planning output

Before writing or execution, the plan reports:

- pack-owned manifest artifacts to create/change/delete/leave;
- known ecosystem contributions when supported;
- exact commands and executables;
- requested filesystem/network/process capabilities;
- approval state;
- unresolved manual actions;
- conflicts with user-owned project files.

## Required tests

- owned manifest templates follow normal artifact planning/ownership;
- exact command argument boundaries survive decode/plan unchanged;
- executable replacement does not rewrite arguments;
- no dependency-map-to-command conversion exists;
- no pack traits/profiles/integration/dependencies sections decode in the baseline manifest;
- existing user manifests are not replaced implicitly;
- ecosystem contribution contracts are typed, visible, conflict-detecting, and non-semantic;
- command changes invalidate approval;
- lifecycle/network/filesystem permissions are enforced;
- output state remains separate from the dependency lock.
