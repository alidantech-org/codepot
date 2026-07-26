# Toolchains, dependencies, and manifests

## Goal

Packs must describe what project environment and dependencies they need without hardcoding one package manager or overwriting user-owned manifests.

## Project toolchains

The project selects the actual toolchain:

```yaml
toolchains:
  node:
    version: ">=20"
    packageManager: pnpm
  dart:
    sdk: ">=3.5.0 <4.0.0"
```

Resolution order for Node package managers:

1. explicit project configuration;
2. existing `packageManager` field in `package.json`;
3. existing lockfile;
4. workspace configuration;
5. compatible pack preference;
6. interactive configuration;
7. error in non-interactive mode when still ambiguous.

CodepotG never silently switches an established project from one package manager to another.

## Pack requirements

Packs should prefer capabilities over exact tools:

```yaml
dependencies:
  node:
    packageManagers:
      requires: [workspaces, lockfile]
      supported: [npm, pnpm, yarn]
      preferred: pnpm
```

A pack requires an exact manager only when its implementation genuinely depends on a unique capability.

When several packs constrain the same project unit, CodepotG intersects their supported capability sets and reports a clear conflict only when no valid tool remains.

## Project units

A repository may contain several independently managed units:

```text
backend/           Node + pnpm
web/               Node + pnpm
packages/api_sdk/  Dart package
```

`codepotg.yaml` may define units and attach packs to them so package-manager choices are scoped rather than assumed global to the repository.

## Ecosystem adapters

Typed ecosystem adapters understand manifests and tools:

- Node project adapter: `package.json`, scripts, dependencies, dev dependencies, exports, workspaces, package-manager metadata, lockfiles;
- Dart project adapter: `pubspec.yaml`, dependencies, dev dependencies, SDK constraints, Flutter sections, assets, workspaces;
- future Python, Cargo, Gradle, and Maven adapters follow the same port.

## Owned versus contributed manifests

A pack may fully template a manifest it owns, for example a new standalone Dart package with its own `pubspec.yaml`.

A pack extending an existing project declares typed contributions instead of replacing the user-owned manifest.

```yaml
integration:
  manifestMode: contribute

dependencies:
  node:
    runtime:
      "@nestjs/swagger": "^8.0.0"
    development:
      prettier: "^3.0.0"
    scripts:
      format: "prettier --write src"
```

The ecosystem adapter validates and applies the desired state.

## Pack traits

Integration behavior is described through independent traits such as:

```yaml
integration:
  createsProject: false
  ownsFolder: true
  contributesFiles: true
  requiresDependencies: true
  requiresBindings: false
  runnableAlone: true
  manifestMode: owned
```

This supports:

- complete runnable projects;
- standalone packages inside a workspace;
- existing-project extensions;
- fragment packs;
- mixed packs that combine several traits.

## Dependency source types

Known ecosystem schemas support normal registry dependencies and explicit sources.

Node examples:

```yaml
dependencies:
  node:
    runtime:
      zod: "^4.0.0"
      company-runtime:
        git:
          url: git+ssh://git@github.com/company/runtime.git
          ref: v3.1.0
```

Dart examples:

```yaml
dependencies:
  dart:
    hosted:
      dio: "^5.0.0"
    packages:
      internal_models:
        git:
          url: git@github.com:company/internal-models.git
          ref: v2.0.0
```

## Installation policy

A pack may declare one of these setup recommendations:

- `declareOnly` — report desired state only;
- `suggest` — show manifest changes and exact actions;
- `ask` — offer to apply changes and install;
- `automatic` — request automatic action under security policy.

A downloaded pack cannot force execution when host or project policy requires approval or denial.

## Lifecycle scripts

Dependency installation can execute third-party lifecycle scripts. The security policy treats lifecycle scripts separately and may:

- allow;
- require approval;
- disable when supported;
- deny installation.

## Planning output

Before modification or command execution, the plan shows:

- manifest files affected;
- exact dependency additions or version conflicts;
- scripts or workspace entries added;
- selected package manager;
- install action and capabilities;
- manual steps when automatic contribution is unsupported.

## Tests

Required tests cover:

- package-manager detection precedence;
- constraint intersection;
- no silent manager switching;
- owned versus contributed manifests;
- duplicate and conflicting dependency declarations;
- workspace registration;
- Node and Dart typed serialization;
- install policy and lifecycle-script security;
- several toolchain units in one project.
