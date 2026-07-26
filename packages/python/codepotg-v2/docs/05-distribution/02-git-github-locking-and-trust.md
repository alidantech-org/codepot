# Git, GitHub, locking, and trust

## Pack locators

Supported project references include:

```yaml
use:
  path: ./packs/server
```

```yaml
use:
  github: alidantech-org/codepotg-nestjs-pack
  ref: v2.1.0
  path: packs/nestjs
```

```yaml
use:
  git:
    url: git@github.com:alidantech-org/private-packs.git
    ref: main
    path: packs/sdk
```

GitHub shorthand is convenience syntax over generic Git resolution.

## Authentication

CodepotG uses the user's or host's existing Git authentication:

- SSH agent;
- SSH keys;
- Git credential manager/helper;
- controlled HTTPS credentials;
- enterprise Git configuration.

Credentials are never written to `codepotg.yaml`, `CodepotgPack.yaml`, `codepotg.lock`, diagnostics, events, cache metadata, or approval records.

## Resolution

A provider resolves:

- repository identity;
- requested ref;
- immutable commit;
- pack subdirectory;
- manifest path;
- pack content digest;
- trust/source metadata;
- controlled local snapshot.

Branches and tags are acceptable authoring inputs, but generation can operate in locked/frozen mode against the resolved commit.

## Lock file

`codepotg.lock` records reproducibility inputs such as:

```yaml
lockVersion: 1
runtime:
  core: 2.0.0
  ir: 2.0
packs:
  server:
    requested:
      repository: git@github.com:alidantech-org/private-packs.git
      ref: v2.1.0
      path: packs/server
    resolved:
      commit: 2741acc937...
      manifestDigest: sha256:...
      contentDigest: sha256:...
plugins:
  language.typescript:
    package: codepotg-language-typescript
    version: 2.0.0
    behaviorVersion: 1
```

The lock excludes credentials and secrets.

## Cache

Git pack snapshots are cached by immutable identity and validated digest. Partial fetches are cleaned safely. Cache reuse must not skip manifest parsing, compatibility checks, command approval checks, or plan validation.

## Private packs

Private packs require no Codepot-hosted credential service. Access succeeds when the user's Git configuration permits the clone/fetch. This supports personal, organization, private, public, and enterprise repositories.

## Command approvals

Downloaded pack commands require approval by default. Approval identity includes:

- repository;
- resolved commit;
- pack subdirectory;
- manifest/content digest;
- exact command/action digest;
- capabilities and environment requests.

A new commit or changed command requires new approval.

## Future site discovery

The Codepot site may index metadata and search information:

- pack ID and description;
- repository and pack path;
- stable tags;
- supported targets/frameworks;
- dependencies and bindings;
- command capabilities;
- docs and verification status.

Initial pack bytes remain in Git. Private packs can stay direct references and need not be indexed.

## Safety tests

Required tests cover:

- local path containment;
- public and controlled private repositories;
- ref-to-commit locking;
- subdirectory validation;
- moved branch drift;
- credential redaction;
- cache corruption/partial fetch cleanup;
- approval invalidation;
- no network in server-safe mode unless the host provides a permitted pack provider.
