# 05 — Distribution, Git packs, and application interfaces

## Batteries included without hardcoding

The final release model has:

- `codepotg-core` — minimal application/domain/plugin contracts for embedded and custom installations;
- `codepotg` — normal batteries-included installation with compatible OpenAPI, TypeScript, Dart, Jinja, and initial SDK packs.

Official defaults remain independently versioned and discovered through the same entry-point system used by third parties.

## Git-hosted packs

Projects may reference local directories, GitHub shorthand, or generic Git repositories. Git/GitHub pack resolution uses existing SSH agents, keys, credential helpers, or controlled HTTPS credentials. Tokens and credentials are never stored in project or lock files.

Branches/tags resolve to immutable commits recorded with pack subdirectory and content/manifest digests in `codepotg.lock`.

A future Codepot site may index searchable public metadata while pack bytes continue to come from Git. Private packs can remain direct Git references using the user's access.

## Python API first

The importable Python API is the primary product interface. It supports filesystem, memory, and archive generation plus sync/async operations, cancellation, structured diagnostics, events, and server-safe policies.

The CLI, configure wizard, MCP tools, HTTP services, playgrounds, and notebooks call the same application services. They do not parse each other's output or shell out to access core behavior.

## Supported operations

- configure project/pack instances;
- validate project and packs;
- inspect plugins, schemas, packs, rules, plans, locks, approvals, and cache;
- resolve/add Git packs;
- generate to memory/archive/filesystem;
- manage command approvals;
- update/check lock state.

There is no v2 old-configuration migration operation. Project and pack authors re-author old files into the documented v2 schemas while the old package remains available for old projects during development.

See the detailed distribution/Git tasks in `../tasks/06-configure-cli-git-and-distribution.md` and the clean-room release plan in `../06-rewrite`.
