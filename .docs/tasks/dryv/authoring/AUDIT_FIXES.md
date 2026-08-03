# dryv-author audit fixes

These fixes were identified during the six-package Dryv connectability audit on 2026-07-27.

## AUTHOR-AUDIT-001 — Use one canonical IR transport

**Status:** fix required

### Finding

`dryv-author` contains a package-local codec with:

```text
format: dryv.ir
version: 1
```

Core owns a different canonical transport consumed by the built-in `ir` source adapter. The author codec also uses a fixed type registry that does not cover all newer public core IR records.

### Required fix

- make author transport delegate to the public `dryv.ir` codec;
- remove the duplicate dataclass/enum registry and duplicate envelope;
- preserve convenient `AuthoringResult.to_json()` / `to_yaml()` methods only as thin core-codec calls;
- add an exact test proving author output is accepted directly by the installed built-in `ir` source adapter;
- add round trips for tags, guidance, field capabilities, value sources, and presentations once authoring supports them.

### Current safe bridge

```text
Author.compile().contract
    -> dryv.ir.contract_to_json()
    -> adapter: ir
```

Do not document `dryv_author.dumps_json()` as an orchestrator input until this task passes.

## AUTHOR-AUDIT-002 — Reproduce synchronized release gates

**Status:** review required

Run from the synchronized checkout:

```bash
python -m pip install -e ../dryv -e '.[dev]'
python -m ruff check src tests
python -m ruff format --check src tests
python -m pytest -vv
python -m mypy src
python -m pyright src
rm -rf build dist
python -m build
```

Then install the real core and author wheels together in a fresh environment and run:

```text
Python authoring -> Author.compile() -> core canonical transport -> built-in ir adapter
```

## AUTHOR-AUDIT-003 — Complete evolved-core authoring coverage

**Status:** planned

The compiler currently covers the implemented structural/behavior foundation. Add public authoring and lowering for the evolved core contracts without private extensions:

- namespaced tags;
- categorized guidance;
- field capabilities;
- value sources;
- presentations and entries.

Each feature requires typed declarations, ref validation, deterministic public IR lowering, core validation, core-codec transport, and a connected pack/template manual example.
