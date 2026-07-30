# 05 — Distribution, pack resolution, and application interfaces

## Documents

- [`01-package-topology-and-defaults.md`](01-package-topology-and-defaults.md) — runtime, CLI, authoring, plugin distributions, versioning, trust, and fresh-install acceptance.
- [`02-git-github-locking-and-trust.md`](02-git-github-locking-and-trust.md) — direct local/Git pack sources, authentication, immutable resolution, `dryv.lock.yaml`, cache, private packs, and approvals.
- [`../01-foundation/02-public-python-api.md`](../01-foundation/02-public-python-api.md) — Python-first runtime facade, sessions, results, events, memory output, and server-safe use.
- [`../tasks/06-configure-cli-git-and-distribution.md`](../tasks/06-configure-cli-git-and-distribution.md) — implementation backlog and acceptance gates.

## Package model

```text
dryv                         runtime and canonical contracts
dryv-cli                     standalone command-line interface
dryv-author                  typed Python authoring frontend
dryv-template-jinja          template-engine plugin
dryv-language-typescript     TypeScript target plugin
dryv-language-dart           Dart target plugin
```

Optional packages are independently versioned and use the same public plugin contracts as third-party packages.

The runtime distribution does not depend on the CLI or authoring frontend. The CLI and all plugin packages depend on the public runtime.

## Direct Git-hosted packs

Projects reference a local folder or a complete Git URL/ref/path directly inside each pack instance. Any compatible Git host is supported; no host-specific shorthand or mutable registry alias is required.

Git resolution uses existing SSH agents, keys, credential helpers, or controlled HTTPS credentials. Credentials never enter project, lock, state, or diagnostic files.

Branches and tags resolve to immutable commits stored with pack subdirectory and content/manifest digests in `dryv.lock.yaml`.

A future marketplace may help users discover packs, but its output is a complete source block inserted into `dryv.yaml`; runtime resolution remains self-contained and reproducible.

## Python API first

The importable runtime API is the primary interface. CLI, configure wizard, MCP, HTTP, playground, IDE, and notebook integrations call the same public operations.

## Planned operations

- load and validate projects, contracts, packs, and plugins;
- inspect plugin capabilities, selectors, plans, imports/exports, locks, state, and approvals;
- resolve local and Git packs;
- generate to memory, archive, or managed filesystem output;
- emit canonical IR transport;
- manage command approvals through a separate trusted runtime;
- update and verify frozen lock state.

There is no compatibility decoder or migration runtime for the archived generator.
