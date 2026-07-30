# Canonical Dryv IR JSON/YAML transport

## Goal

`dryv-author` compiles to an immutable core contract. The Dryv runtime may serialize that contract as readable JSON or YAML for debugging, review, caching, transport, signing, fixtures, and direct semantic reuse.

## Distinction

```text
Authoring refs, builders, and Pydantic models
    → compiler-only values

Dryv Contract
    → primary in-memory semantic representation

Canonical IR document
    → optional portable representation
```

Transport must never serialize authoring state.

## Envelope

A canonical document includes an explicit format, IR version, behavior versions, and contract payload:

```json
{
  "format": "dryv.ir",
  "irVersion": "...",
  "behaviorVersions": {},
  "contract": {}
}
```

Relations use explicit semantic references where a portable reference is clearer than a raw string.

## Runtime API

```python
from dryv.ir import (
    contract_from_document,
    contract_from_json,
    contract_from_yaml,
    contract_to_document,
    contract_to_json,
    contract_to_yaml,
)

result = author.compile()
contract = result.require_contract()

json_text = contract_to_json(contract)
yaml_text = contract_to_yaml(contract)
```

The author package returns a `Contract`; it does not own a second transport codec.

## Guarantees

- strict IR and behavior versions;
- deterministic ordering;
- canonical semantic IDs;
- JSON-compatible scalars and bounded immutable values;
- duplicate-key-safe YAML parsing;
- safe YAML loading without arbitrary object construction;
- strict unknown-field diagnostics;
- no class, module, callable, or object-address values;
- round-trip equality;
- JSON/YAML semantic parity;
- core validation after decoding;
- stable canonical JSON digest;
- readable pretty JSON and YAML output;
- source-aware diagnostics for malformed transported documents.

## Input role

A canonical document already contains normalized Dryv semantics:

```text
IR document → strict decode → immutable Contract → core validation
```

It does not repeat authoring compilation.

## Ownership

The canonical codec is a public Dryv runtime facility shared by authoring tools, hosts, fixtures, caches, and the built-in IR loader. `dryv-author` delegates to that facility and must not maintain a package-local schema registry.

A generic `dataclasses.asdict()` dump does not qualify as canonical transport.
