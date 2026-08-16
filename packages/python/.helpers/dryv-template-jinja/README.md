# dryv-template-jinja

`dryv-template-jinja` is an independent Jinja **Render Client** for Dryv. It receives an already-selected template plus canonical JSON context and returns rendered artifact bytes. It does not import Dryv Runtime, understand Canonical IR semantics, select templates, build context, or write project files.

## Session boundary

```text
Dryv Runtime / dryv-api
      |
      | Render Session request
      v
JinjaRenderSession
      |
      | rendered logical outputs + hashes + diagnostics
      v
Dryv Runtime
```

The structural session contract is exposed by `JinjaRenderSession` and the process form is available with:

```bash
python -m dryv_template_jinja.stdio
```

The JSONL process supports `hello`, `render`, `cancel`, and `shutdown`. It advertises:

- renderer id/version;
- capability `jinja/v1`;
- render/context protocol versions;
- supported template media types;
- deterministic renderer fingerprint;
- maximum concurrency.

## Safety and determinism

The client uses a sandboxed Jinja environment with `StrictUndefined`, clears default globals, accepts only the context supplied by Runtime, and returns stable SHA-256 artifact content identities. It has no Project Client filesystem authority.

## Validation

```bash
uv run --all-packages pytest packages/python/dryv-template-jinja/tests/contracts/test_render_session.py
uv run --all-packages ruff check packages/python/dryv-template-jinja
```
