# dryv-author

`dryv-author` is the Python authoring implementation for Dryv. It gives Python users a typed API for describing software and compiles that authored meaning into the same versioned Canonical Dryv Runtime IR consumed by every Dryv Runtime.

## Boundary

```text
Python author source
      |
      v
dryv-author compiler
      |
      v
Canonical Dryv Runtime IR
      |
      v
Dryv Runtime
```

`dryv-author` defines software meaning. It does **not** select packs, build template context, render templates, choose project output paths, or write generated files.

The independent backend process is available with:

```bash
python -m dryv_author.stdio
```

That JSONL session exposes Author Backend capabilities, receives logical Python source resources, compiles the source, and emits Canonical IR plus progress/diagnostics. The backend process never hosts Dryv Runtime and does not need to know which packs or Render Clients will be used later.

## Author source contract

The process backend accepts trusted Python author source that exposes either:

```python
def build_author() -> Author:
    ...
```

or a module-level `AUTHOR` value.

Example:

```python
from dryv_author import Author, field


def build_author() -> Author:
    author = Author("accounts")
    group = author.group("Users")
    author.schema(
        "User",
        {"email": field(str, required=True)},
        group=group,
    )
    return author
```

The compiler emits Canonical IR; Runtime remains the semantic authority for downstream validation, indexing, inspection, planning, caching, and generation.

## Precompiled IR

Projects that already have `dryv.ir.json`, YAML, or JSONL do not require an Author Backend at build time. The Runtime bypasses Authoring completely for precompiled Canonical IR.

## Validation

```bash
uv run --all-packages pytest packages/python/dryv-author/tests
uv run --all-packages ruff check packages/python/dryv-author
```
