# Canonical Dryv IR JSON/YAML transport

## Purpose

The closed in-memory IR is portable. A validated `Contract` may be serialized for debugging, review, sharing, caching, signing, fixtures, or later generation.

Transport does not create another semantic model:

```text
Contract
├── canonical JSON
├── readable YAML
└── strict IR loader
```

Decoding reconstructs the same immutable `dryv.ir.Contract` used by selectors, planners, packs, and templates.

## Public API

```python
from dryv.ir import (
    contract_from_document,
    contract_from_json,
    contract_from_yaml,
    contract_to_document,
    contract_to_json,
    contract_to_yaml,
)
```

Round-trip guarantee:

```python
decoded = contract_from_json(contract_to_json(contract))
assert decoded == contract
```

The same guarantee applies to YAML.

## Envelope

```json
{
  "format": "dryv.ir",
  "irVersion": "dryv.ir/2.0.0",
  "contract": {
    "$type": "Contract"
  }
}
```

The exact format and IR version are required. Unknown envelope fields fail.

## Record encoding

The transport is explicit and unambiguous:

```text
{"$type": "Schema", ...}          typed immutable record
{"$ref": "users.schema.User"}     SemanticId
{"$name": "User"}                 Name
{"$enum": "SchemaKind", "value": "object"}
```

This representation is intentionally verbose. It is designed to be readable, strict, deterministic, portable, and safe to share between processes.

Authoring builders, Pydantic models, decorators, functions, registries, parser nodes, template engines, and target adapters never appear.

## Canonical JSON

Compact JSON is suitable for hashing:

```python
payload = contract_to_json(contract, pretty=False)
```

Guarantees:

- UTF-8;
- sorted object keys;
- deterministic enum and type discriminators;
- finite numbers only;
- no object addresses;
- no Python class-module names;
- core validation before encoding.

Pretty JSON is intended for debugging and fixtures.

## YAML

```python
payload = contract_to_yaml(contract)
```

YAML uses a safe loader and the same semantic document shape as JSON.

It rejects:

- duplicate mapping keys;
- recursive alias graphs;
- unknown types and enum names;
- unknown record fields;
- unsupported versions;
- non-string object keys;
- non-finite numbers;
- invalid semantic relationships.

## Resource limits

The codec enforces bounded decoded depth and value counts. The built-in file loader additionally limits source-document bytes. Exact limits are behavior-versioned and covered by tests.

## Built-in IR loader

The runtime distribution registers:

```text
entry-point group: dryv.source_adapters
name: ir
plugin id: ir
```

Project usage:

```yaml
sources:
  contract:
    adapter: ir
    file: contracts/application.dryv.json
```

YAML is also accepted:

```yaml
sources:
  contract:
    adapter: ir
    file: contracts/application.dryv.yaml
```

The loader:

1. reads an authorized file or host-supplied in-memory source;
2. rejects unknown loader options;
3. decodes the strict transport;
4. reconstructs immutable IR;
5. runs core validation;
6. derives its digest from compact canonical JSON.

It does not infer, repair, or add semantics.

## In-memory authoring

Canonical files are optional. A Python authoring frontend or host application may provide the `Contract` directly to the runtime once the public contract-provider API is enabled.

## Compatibility

IR migrations are never implicit. An unsupported `irVersion` fails with a stable diagnostic. Future migration tools may convert one complete transport version to another explicitly, but ordinary loading never silently changes semantic meaning.
