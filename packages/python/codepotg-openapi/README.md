# codepotg-openapi

`codepotg-openapi` is the typed OpenAPI 3.0/3.1 source adapter for CodepotG v2. It loads controlled YAML or JSON sources, resolves references within host authority, decodes typed `x-codegen` version 2 metadata, and returns the immutable closed CodepotG semantic kernel.

## Installation

```bash
python -m pip install codepotg-core codepotg-openapi
```

The package registers:

```toml
[project.entry-points."codepotg.source_adapters"]
openapi = "codepotg_openapi.plugin:create_plugin"
```

## Safe default authority

`create_plugin()` permits in-memory sources and absolute local files. Local references must stay below the root document's directory. Network schemes, unsupported URI schemes, relative root paths, and path escapes are rejected. Network or virtual external documents require a host-injected controlled loader:

```python
from codepotg_openapi import OpenApiSourceAdapter
from codepotg_openapi.loading import SourcePolicy

adapter = OpenApiSourceAdapter(
    reference_loader=host_loader,
    source_policy=SourcePolicy(local_root=approved_root),
)
```

Request options cannot grant their own host, network, or filesystem authority.

## Options

| Option | Values/default |
|---|---|
| `validation` | `strict` (default), `tolerant` |
| `externalReferences` | `deny`, `localOnly` (default), `controlled` |
| `grouping` | `tags`, `explicitThenTags` (default) |
| `multiTagPolicy` | `first` (default), `explicitRequired` |
| `operationIds` | `require`, `deterministicFallback` (default) |
| `xCodegenPolicy` | `deny`, `tolerant` (default), `strict` |
| `maxSourceBytes` | positive integer, default `8388608` |
| `maxReferenceDepth` | positive integer, default `64` |
| `maxDocuments` | positive integer, default `128` |
| `preserveUnknownExtensions` | boolean, default `false` |
| `maxPreservedDepth` | positive integer, default `8` |
| `maxPreservedItems` | positive integer, default `2048` |

Unknown keys and wrong value types are errors. There are no target language, framework, template, pack, selector, output path, writer, or command options.

## Dependencies

- `codepotg-core >= 2.0.0a1, < 2.1` supplies only the published source-adapter, diagnostics, plugin, version, testing, and closed-IR contracts.
- `PyYAML >= 6.0, < 7` supplies `SafeLoader` YAML composition with node marks. The adapter converts nodes into package-private JSON-compatible values, rejects duplicate keys and unsafe tags, and never exposes PyYAML objects.

The package does not depend on CodepotG 1.0.0, Jinja, target adapters, template packs, CLI libraries, writers, or network clients.

## Determinism

The result digest covers canonical semantic contents of every loaded document, all decoded options, adapter/package/API/IR/behavior versions, OpenAPI policy, `x-codegen` version, and injected reference-authority identity. Equivalent JSON and YAML documents have the same semantic digest. Their raw byte hashes and format-specific provenance spans may differ.

See [`docs/support/README.md`](docs/support/README.md) for the mapping and explicit public-core blockers. Benchmarks are documented in [`benchmarks/README.md`](benchmarks/README.md).
