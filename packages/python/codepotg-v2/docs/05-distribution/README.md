# 05 — Distribution, Git packs, and application interfaces

## Documents

- [`01-package-topology-and-defaults.md`](01-package-topology-and-defaults.md) — minimal core, batteries-included defaults, independent plugins, versioning, trust, and fresh-install acceptance.
- [`02-git-github-locking-and-trust.md`](02-git-github-locking-and-trust.md) — local/Git/GitHub locators, authentication, immutable resolution, lock files, cache, private packs, approvals, and future site discovery.
- [`../01-foundation/02-public-python-api.md`](../01-foundation/02-public-python-api.md) — Python-first facade, sessions, results, events, memory output, async operation, and server-safe use.
- [`../tasks/06-configure-cli-git-and-distribution.md`](../tasks/06-configure-cli-git-and-distribution.md) — implementation backlog and acceptance gates.

## Batteries included without hardcoding

The final release model has:

- `codepotg-core` — minimal application/domain/plugin contracts for embedded and custom installations;
- `codepotg` — normal batteries-included installation with compatible OpenAPI, TypeScript, Dart, Jinja, and initial SDK packs.

Official defaults remain independently versioned and discovered through the same entry-point system used by third parties.

## Git-hosted packs

Projects may reference local directories, GitHub shorthand, or generic Git repositories. Git/GitHub resolution uses existing SSH agents, keys, credential helpers, or controlled HTTPS credentials. Credentials are never stored in project or lock files.

Branches/tags resolve to immutable commits recorded with pack subdirectory and content/manifest digests in `codepotg.lock`. A future Codepot site may index searchable public metadata while pack bytes continue to come from Git. Private packs can remain direct references using the user's access.

## Python API first

The importable Python API is the primary product interface. It supports filesystem, memory, and archive generation plus sync/async operations, cancellation, structured diagnostics, events, and server-safe policies.

The CLI, configure wizard, MCP tools, HTTP services, playgrounds, and notebooks call the same application services.

## Supported operations

- configure project/pack instances;
- validate project and packs;
- inspect plugins, schemas, packs, rules, plans, locks, approvals, and cache;
- resolve/add Git packs;
- generate to memory/archive/filesystem;
- manage command approvals;
- update/check lock state.

There is no v2 old-configuration decoder or migration operation. Project and pack authors re-author old files into the documented v2 schemas while the old package remains available for old projects during development.
