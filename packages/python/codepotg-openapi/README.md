# codepotg-openapi

`codepotg-openapi` is the OpenAPI 3.0/3.1 source adapter for CodepotG v2. Version `2.0.0a2` provides a working public `SourceAdapter`: it loads controlled JSON or YAML, resolves authorized references inside one normalization session, normalizes the supported standard OpenAPI subset into the closed CodepotG kernel, runs core validation, and returns a deterministic `SourceAdapterResult`.

Typed `x-codegen`, security/access normalization, storage, views, events/listeners, hooks, workflows, and benchmarks are **not implemented in this release**. See [the support matrix](docs/support/README.md).

## Entry point

```toml
[project.entry-points."codepotg.source_adapters"]
openapi = "codepotg_openapi.plugin:create_plugin"
```

```python
from codepotg.api import CancellationToken
from codepotg.ports import SourceAdapterRequest
from codepotg_openapi import OpenApiSourceAdapter

adapter = OpenApiSourceAdapter()
result = adapter.normalize(
    SourceAdapterRequest(
        source_id="petstore",
        content='{"openapi":"3.1.0","info":{"title":"Pets","version":"1"},"paths":{}}',
    ),
    CancellationToken(),
)

assert result.contract is not None
assert result.digest
```

`create_plugin()` and the installed `codepotg.source_adapters/openapi` entry point return the same adapter type.

## Safe source authority

The default adapter accepts in-memory documents and absolute local files. A local root document authorizes references only beneath its parent directory unless the host supplies a narrower `SourcePolicy.allowed_root`. Relative root paths, path escapes, unsupported schemes, and network references are denied.

A host can explicitly provide controlled external content:

```python
from pathlib import Path

from codepotg_openapi import OpenApiSourceAdapter
from codepotg_openapi.loading import CallableReferenceLoader, SourcePolicy

adapter = OpenApiSourceAdapter(
    reference_loader=CallableReferenceLoader(host_loader, authority_id="approved-catalog-v1"),
    source_policy=SourcePolicy(allowed_root=Path("/srv/contracts")),
)
```

Request options cannot grant filesystem or network authority. Reference bytes and parsed documents are cached only inside one `normalize()` call; reusing an adapter starts a fresh session.

## Options

| Option | Values/default |
|---|---|
| `validation` | `strict` (default), `tolerant` |
| `externalReferences` | `deny`, `localOnly` (default), `controlled` |
| `grouping` | `tags`, `explicitThenTags` (default) |
| `multiTagPolicy` | `first` (default), `explicitRequired` |
| `operationIds` | `require`, `deterministicFallback` (default) |
| `xCodegenPolicy` | `tolerant` (default), `strict`, `deny`; typed mapping is not implemented, so tolerant warns and strict/deny fail |
| `maxSourceBytes` | positive integer, default `8388608` |
| `maxReferenceDepth` | positive integer, default `64` |
| `maxDocuments` | positive integer, default `128` |
| `maxYamlDepth` | positive integer, default `128` |
| `maxYamlNodes` | positive integer, default `100000` |
| `maxYamlAliases` | positive integer, default `10000` |
| `preserveUnknownExtensions` | boolean, default `false` |
| `maxPreservedDepth` | positive integer, default `8` |
| `maxPreservedItems` | positive integer, default `2048` |

Unknown keys and wrong value types are errors. No target language, framework, template, selector, output-path, writer, or command options exist.

## Determinism and validation

The result digest includes every loaded document's canonical semantic content, all decoded behavior options, adapter/package/plugin/IR behavior versions, OpenAPI version policy, and the host reference-authority identity. Equivalent JSON and YAML with the same `source_id` produce the same semantic contract and digest. Format-specific source spans may differ.

Before success, the adapter calls `codepotg.ir.validate_contract`. Any adapter or core error returns `contract=None`, `digest=None`, and sorted diagnostics. Cancellation is returned as `OA_CANCELLED` rather than leaking an internal exception.

## Dependencies

- `codepotg-core >= 2.0.0a1, < 2.1`, through published `codepotg.*` namespaces only.
- `PyYAML >= 6.0, < 7`, using `SafeLoader` composition followed by bounded package-private conversion.

The package does not import CodepotG v1, target-language adapters, template engines, packs, writers, CLI libraries, or network clients.
