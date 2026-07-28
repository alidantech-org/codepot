# dryv-author

`dryv-author` is the typed Python authoring frontend for Dryv.

It lets developers define contracts, groups, reusable properties, structural schemas, projections, operations, policies, events, storage mappings, views, workflows, guidance, and namespaced tags through a concise Python API. Compilation produces the same closed immutable `dryv.ir.Contract` consumed by the Dryv runtime.

## Core flow

```text
concise typed Python declarations
              ↓
     typed references and compiler passes
              ↓
      immutable Dryv Contract
              ↓
     Dryv planning and generation runtime
```

The in-memory contract is the primary result. JSON and YAML emission belongs to the Dryv runtime as optional transport, debugging, review, caching, and sharing functionality.

## Responsibility boundary

`dryv-author` owns:

- typed declaration objects;
- authoring references;
- declaration validation;
- deterministic compiler passes;
- Pydantic model interpretation;
- conversion into public Dryv IR;
- authoring diagnostics.

It does not:

- create a second semantic graph;
- replace or extend the Dryv kernel;
- select packs, templates, or output paths;
- render target-language syntax;
- write generated project files;
- manage generation ownership state;
- execute commands;
- own CLI behavior;
- expose mutable authoring builders to templates;
- use process-global decorator or reference registries.

## Example

```python
from dryv_author import Author, field


def build_contract():
    author = Author("Accounts")
    author.schema(
        "User",
        {
            "id": field(str, readonly=True),
            "email": field(str),
            "display_name": field(str, optional=True),
        },
    )
    return author.compile().require_contract()
```

A host can pass the resulting contract directly to the Dryv runtime. A project configuration may later resolve an equivalent Python callable through the runtime contract-provider interface.

## Verification

From `packages/python/dryv-author`:

```bash
python -m pip install -e ../dryv -e ".[dev]"
python -m ruff check src tests
python -m ruff format --check src tests
python -m pytest -q
python -m mypy src tests
python -m pyright
python -m build
```

## Documentation

Start with:

- [`docs/IDEA.md`](docs/IDEA.md)
- [`docs/README.md`](docs/README.md)
- [`docs/design/00-authoring-architecture.md`](docs/design/00-authoring-architecture.md)
- [`docs/tasks/00-master-plan.md`](docs/tasks/00-master-plan.md)
