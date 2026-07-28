# Canonical Codepot IR JSON/YAML transport

## Goal

`dryv-author` must compile to an immutable core contract and support readable JSON/YAML for debugging, review, caching, transport, and reuse as a direct semantic input.

## Distinction

```text
Authoring refs/builders/Pydantic models
    → compiler-only values

Core IR document
    → portable semantic contract
```

Transport must never serialize authoring state.

## Envelope

A canonical document includes:

```json
{
  "format": "codepot-ir",
  "irVersion": "...",
  "behaviorVersions": {},
  "contract": {}
}
```

Relations are encoded as explicit semantic `$ref` objects where a portable reference is clearer than a raw string.

## API

Planned API:

```python
result = author.compile()
result.to_document()
result.to_json(pretty=True)
result.to_yaml()

contract_to_document(contract)
contract_to_json(contract)
contract_to_yaml(contract)
contract_from_document(document)
contract_from_json(text)
contract_from_yaml(text)
```

## Guarantees

- strict IR and behavior versions;
- deterministic ordering;
- canonical semantic IDs;
- JSON-compatible scalars and bounded immutable values;
- duplicate-key-safe YAML parsing;
- safe YAML loading without arbitrary object construction;
- strict unknown-field diagnostics;
- no class/module/callable/object-address values;
- round-trip equality;
- JSON/YAML semantic parity;
- core validation after decoding;
- stable canonical JSON digest;
- readable pretty JSON and YAML output;
- source-aware diagnostics for malformed transported documents.

## Input role

A Codepot IR JSON/YAML document is already normalized semantics:

```text
IR document → strict decode → immutable Contract → core validation
```

It does not repeat OpenAPI inference or authoring compilation.

## Ownership

The canonical codec ideally becomes a public core facility because every source and runtime may use it. The author package may implement the first codec only if it uses public IR contracts, is fully round-trippable, and is documented as the canonical Codepot IR format rather than an author-specific document.

No generic `dataclasses.asdict()` dump qualifies as canonical transport.
