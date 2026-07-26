# 05 — Distribution, Git packs, and application interfaces

## Batteries included without hardcoding

The final release model has a minimal core distribution and a normal `codepotg` distribution that installs compatible defaults. A standard installation should immediately provide OpenAPI, TypeScript, Dart, Jinja, and initial SDK packs while all components remain independently versioned and discovered through entry points.

The current legacy `packages/python/codepotg` package is not changed during the rewrite. The final package cutover happens only after parity and migration gates pass.

## Git and GitHub pack sources

A project may reference a local pack, a GitHub shorthand, or a generic Git repository:

```yaml
packs:
  server:
    use:
      github: alidantech-org/codepotg-nestjs-pack
      ref: v1.4.0
      path: packs/nestjs
```

```yaml
packs:
  privateSdk:
    use:
      git:
        url: git@github.com:alidantech-org/private-packs.git
        ref: v2.0.0
        path: packs/sdk
```

CodepotG uses normal Git authentication such as SSH agents, SSH keys, credential helpers, and existing HTTPS credentials. Tokens are never stored in `codepotg.yaml`. GitHub is initially a Git host, not a mandatory registry API.

Tags and branches resolve to immutable commits recorded in `codepotg.lock`. Cache and command approvals include repository URL, resolved commit, pack path, manifest digest, and command digest. Moving branches warn in reproducible or production mode.

A future Codepot site may index searchable public metadata and map friendly pack names to Git sources without hosting pack contents or private credentials.

## Python API first

The supported Python facade is the primary product interface:

```python
from codepotg import CodepotG

app = CodepotG.standard()
result = app.generate_from_file("codepotg.yaml")
```

Programmatic requests also support in-memory sources and outputs for tests, notebooks, playgrounds, servers, and MCP. Runtime instances are reusable where immutable; every generation creates an isolated session. Synchronous and asynchronous APIs support cancellation, deadlines, structured diagnostics, and event sinks.

## Thin frontends

- The CLI parses arguments, calls application services, renders diagnostics, and chooses exit codes.
- MCP tools call the Python API directly and return structured results.
- HTTP workers and playgrounds use in-memory writers and host-controlled security policies.
- No frontend parses CLI output or shells out to the `codepotg` command to access core behavior.

Operations exposed consistently include configure, validate, migrate configuration, inspect plans, list plugins, describe packs, generate to memory, generate transactionally to disk, and inspect or clear caches under host policy.
