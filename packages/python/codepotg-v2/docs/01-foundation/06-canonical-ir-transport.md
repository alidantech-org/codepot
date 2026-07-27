# Canonical Codepot IR JSON/YAML transport

## Purpose

The closed in-memory IR is portable. A validated `Contract` can be serialized for debugging, review, sharing, caching, signing, fixtures, or later generation without passing through OpenAPI again.

Transport does not create another semantic model:

```text
Contract
├── canonical JSON
├── readable YAML
└── strict IR source adapter
```

The decoded result is the same immutable `codepotg.ir.Contract` used by source adapters, selectors, planners, and templates.

## Public API

```python
from codepotg.ir import (
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
  "format": "codepot-ir",
  "irVersion": "codepotg.ir/2.0.0",
  "contract": {
    "$type": "Contract"
  }
}
```

The exact IR version is required. Unknown envelope fields fail.

## Record encoding

The transport is explicit and unambiguous:

```text
{"$type": "Schema", ...}          typed immutable record
{"$ref": "users.schema.User"}     SemanticId
{"$name": "User"}                 Name
{"$enum": "SchemaKind", "value": "object"}
```

This representation is intentionally verbose. It is designed to be:

- readable in reviews;
- strict during reconstruction;
- independent of Python module paths;
- deterministic;
- round-trippable;
- safe to share between processes.

Python authoring classes, Pydantic models, decorators, functions, registries, parser nodes, and target adapters never appear.

## Canonical JSON

Compact canonical JSON is suitable for hashing:

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

The current codec enforces:

```text
maximum decoded depth: 128
maximum decoded values: 500,000
```

The built-in source adapter additionally limits one source document to 32 MiB.

## Built-in source adapter

The core distribution registers:

```text
entry-point group: codepotg.source_adapters
name: ir
plugin id: ir
alias: codepot-ir
```

Project usage:

```yaml
sources:
  contract:
    adapter: ir
    file: contracts/application.codepot.json
```

YAML is also accepted:

```yaml
sources:
  contract:
    adapter: ir
    file: contracts/application.codepot.yaml
```

The adapter:

1. reads an absolute host-authorized file or in-memory source;
2. rejects adapter options;
3. decodes the strict transport;
4. reconstructs immutable IR;
5. runs core validation;
6. creates a digest from compact canonical JSON.

It does not infer, normalize, repair, or add semantics.

## Difference from OpenAPI

```text
OpenAPI
→ source interpretation and normalization
→ Contract
```

```text
Codepot IR JSON/YAML
→ strict reconstruction
→ Contract
```

OpenAPI is a source format. Canonical Codepot IR is the already-compiled semantic contract.

## Compatibility

IR migrations are not performed implicitly. An unsupported `irVersion` fails with a stable diagnostic.

Future migration tooling may convert one complete transport version to another explicitly. The ordinary source adapter never silently changes semantic meaning.
