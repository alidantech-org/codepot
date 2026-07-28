# 05 — Distribution, direct Git packs, and application interfaces

## Documents

- [`01-package-topology-and-defaults.md`](01-package-topology-and-defaults.md) — minimal core, batteries-included defaults, independent plugins, versioning, trust, and fresh-install acceptance.
- [`02-git-github-locking-and-trust.md`](02-git-github-locking-and-trust.md) — direct `source.local`/`source.git`, authentication, immutable resolution, `dryv.lock.yaml`, cache, private packs, approvals, and future discovery.
- [`../01-foundation/02-public-python-api.md`](../01-foundation/02-public-python-api.md) — Python-first facade, sessions, results, events, memory output, async operation, and server-safe use.
- [`../tasks/06-configure-cli-git-and-distribution.md`](../tasks/06-configure-cli-git-and-distribution.md) — implementation backlog and acceptance gates.

## Batteries included without hardcoding

The release model has:

- `dryv` — minimal application/domain/plugin contracts;
- `dryv` — normal installation with compatible OpenAPI, TypeScript, Dart, Jinja, and initial SDK packs.

Official defaults remain independently versioned and use the same plugin contracts as third-party packages.

## Direct Git-hosted packs

Projects reference a local folder or a complete Git URL/ref/path directly inside each pack instance. GitHub is supported as a normal Git host; no GitHub shorthand or mutable registry alias is required.

Git resolution uses existing SSH agents, keys, credential helpers, or controlled HTTPS credentials. Credentials never enter project or lock files.

Branches and tags resolve to immutable commits stored with pack subdirectory and content/manifest digests in `dryv.lock.yaml`.

A future site may help users discover packs, but its output is a complete source block inserted into `dryv.yaml`; runtime resolution stays self-contained.

## Python API first

The importable Python API remains the primary interface. CLI, configure wizard, MCP, HTTP, playground, and notebook integrations call the same services.

## Supported operations

- configure project pack instances;
- validate project and pack manifests;
- inspect packs, plans, selectors, imports/exports, locks, approvals, and cache;
- add/resolve local and Git packs;
- generate to memory, archive, or filesystem;
- manage command approvals;
- update/check frozen lock state.

There is no v2 old-configuration decoder or migration runtime.
