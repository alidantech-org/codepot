# dryv-cli

Reference Project Client for Dryv. A normal local installation hides API and renderer topology behind four commands:

```bash
dryv validate
dryv compile
dryv plan
dryv generate
```

Example `dryv.yaml`:

```yaml
apiVersion: dryv.dev/v1
name: shop
source:
  author: software.py:build
packs:
  api:
    source:
      local: packs/typescript-api
    output: generated
```

`dryv generate` resolves/compiles Canonical IR, starts a temporary loopback dryv-api when no `--api` is supplied, starts required local renderer helpers such as Jinja, watches build progress, verifies streamed or bundled artifact bytes, computes a local change set, and applies safe generated changes. Runtime remains authoritative for Dryv semantics and planning.

Useful generation controls:

```bash
dryv generate --dry-run
dryv generate --delivery bundle
dryv generate --force
```

`--force` is explicit because existing unmanaged files and locally modified managed files are conflicts by default.
