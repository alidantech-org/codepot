# Local and Git pack sources, locking, and trust

## Direct pack sources

Every pack instance declares its source directly. There is no registry alias or `use` mapping.

Local pack:

```yaml
packs:
  repositories:
    source:
      local: ./packs/typeorm-repositories
```

Git pack at repository root:

```yaml
packs:
  flutterSdk:
    source:
      git: https://github.com/alidantech-org/dryv-pack-flutter-sdk.git
      ref: v1.4.2
```

Git monorepo pack:

```yaml
packs:
  typescriptSdk:
    source:
      git: https://github.com/alidantech-org/dryv-packs.git
      ref: typescript-sdk/v2.4.1
      path: packs/typescript-sdk
```

Private SSH source:

```yaml
source:
  git: git@github.com:alidantech-org/private-dryv-packs.git
  ref: main
  path: packs/internal-backend
```

## Source rules

A pack source has exactly one form:

```yaml
source:
  local: path
```

or:

```yaml
source:
  git: repository-url
  ref: branch-tag-or-commit
  path: optional/repository/subdirectory
```

Rules:

- `local` is relative to `dryv.yaml`;
- `git` is a normal Git HTTPS or SSH URL;
- `ref` is required for Git sources;
- `path` is optional and must remain inside the resolved snapshot;
- `local` and `git` cannot appear together;
- pack identity/version comes from `DryvPack.yaml`;
- the project pack key is only a local instance name.

A future marketplace may help users discover packs, but it inserts a complete direct `source` block. Runtime resolution never depends on a mutable registry alias.

## Authentication

Dryv uses existing Git authentication:

- SSH agent and keys;
- Git credential manager/helper;
- controlled HTTPS credentials;
- enterprise Git configuration.

Credentials are never written to project configuration, pack manifests, lock files, diagnostics, events, cache metadata, ownership state, or approvals.

## Resolution

### Local

The provider:

1. resolves the directory relative to the project;
2. validates containment and manifest presence;
3. snapshots the pack for the run;
4. reads identity/version;
5. calculates manifest/content digests.

The snapshot prevents a mid-run edit from producing an inconsistent plan.

### Git

The provider:

1. validates the URL, ref, and optional path;
2. fetches through controlled Git infrastructure;
3. resolves the branch, tag, or commit to an exact commit;
4. snapshots only the resolved repository state;
5. validates the pack subdirectory and manifest;
6. calculates manifest/content digests;
7. stores the immutable snapshot in cache.

A mutable ref may appear in `dryv.yaml`, but a locked run uses the exact commit recorded in `dryv.lock.yaml`.

## `dryv.lock.yaml`

The lock is generated and should not be hand-authored.

```yaml
apiVersion: dryv.dev/lock/v1

project: defytickets-generated

runtime:
  dryv: 2.0.0
  ir: 2.0
  namingBehavior: 1
  selectionBehavior: 1

packs:
  backendRepositories:
    source:
      local: ./packs/typeorm-repositories
    pack:
      id: alidantech/typeorm-repositories
      version: 1.0.0
    manifestDigest: sha256:1111111111111111111111111111111111111111111111111111111111111111
    contentDigest: sha256:2222222222222222222222222222222222222222222222222222222222222222

  typescriptSdk:
    source:
      git: https://github.com/alidantech-org/dryv-packs.git
      ref: typescript-sdk/v2.4.1
      commit: 53e69ea110cf7739d54782d776be63ab46dfe243
      path: packs/typescript-sdk
    pack:
      id: alidantech/typescript-sdk
      version: 2.4.1
    manifestDigest: sha256:3333333333333333333333333333333333333333333333333333333333333333
    contentDigest: sha256:4444444444444444444444444444444444444444444444444444444444444444

plugins:
  source.ir:
    package: dryv
    version: 2.0.0
    behavior: 1
  language.typescript:
    package: dryv-language-typescript
    version: 2.0.0
    behavior: 1
  template.jinja:
    package: dryv-template-jinja
    version: 2.0.0
    behavior: 1
```

The lock records:

- project/runtime behavior identity;
- each project-local pack instance;
- original local path or Git URL/ref/path;
- exact Git commit where applicable;
- discovered pack ID/version;
- manifest and content digests;
- plugin and behavior versions that affect planning/output.

The lock excludes credentials, environment secrets, generated files, generated file hashes, and approval tokens. Output ownership hashes belong to `.dryv/generation-state.json`.

## Drift rules

A locked run fails when:

- the exact locked commit is unavailable;
- local pack content differs in frozen mode;
- the selected path no longer contains the locked pack identity;
- manifest/content digests differ;
- behavior/plugin versions are incompatible;
- a downloaded pack command changed and lacks renewed approval.

Development commands may explicitly refresh the lock. Frozen mode never updates it silently.

## Cache

Pack snapshots are cached by immutable identity and content digest, not mutable branch names.

Cache reuse still performs manifest parsing, compatibility validation, digest validation, command approval checks, and plan validation. Partial fetches and invalid snapshots are removed safely.

## Private packs

Private packs require no Dryv-hosted credential service. Resolution succeeds when the user's Git environment can fetch the repository. Public, private, organization, personal, and enterprise Git hosts use the same source shape.

## Command approvals

Downloaded pack commands require approval by default. Approval identity includes:

- repository URL or local snapshot identity;
- exact commit for Git sources;
- pack subdirectory;
- manifest/content digests;
- exact executable reference and argument list;
- requested environment/filesystem/network capabilities.

Any identity or command change requires new approval.

## Required safety tests

- local path containment and snapshot stability;
- HTTPS and SSH Git sources;
- branch/tag/commit resolution;
- required Git ref validation;
- monorepo subdirectory containment;
- moved ref and changed local-content drift;
- credential redaction;
- private repository resolution through existing Git credentials;
- cache corruption and partial-fetch cleanup;
- lock serialization and frozen mode;
- command approval invalidation;
- no registry alias drift;
- no network in server-safe mode unless a permitted provider is supplied.
