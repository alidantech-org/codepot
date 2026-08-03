# Supported language adapters

This page records adapters that exist in CodepotG today. It is intentionally separate from the universal adapter catalog, which describes possible future targets rather than release support.

## Support levels

| Adapter | Aliases | Contract | Native templates | Package metadata | Import planner | Native gate |
| --- | --- | --- | --- | --- | --- | --- |
| TypeScript | `ts` | Stable | Existing bundled/project packs | npm-oriented | TypeScript planner | Existing test suite |
| Dart | — | Stable | Existing bundled/project packs | pub-oriented | Dart planner | Existing test suite |
| Debug text | `txt`, `md` | Stable inspection adapter | Debug reports | Not applicable | Markdown links | Existing test suite |
| Python | `py` | Implemented, validation pending | Models, enums, operation client | `pyproject.toml` | Python imports | `compileall` |
| Java | `jvm-java` | Implemented, validation pending | Records, enums, operation client | Maven `pom.xml` | Java imports | `javac` |
| C# | `c#`, `cs`, `dotnet` | Implemented, validation pending | Records, enums, operation client | `.csproj` | C# `using` directives | `dotnet build` |
| Go | `golang` | Implemented, validation pending | Structs, enums, operation client | `go.mod` | Go imports | `gofmt` |
| Rust | `rs` | Implemented, validation pending | Structs, enums, operation client | `Cargo.toml` | Rust `use` paths | `rustfmt` |

“Implemented, validation pending” means the adapter, typed contract enrichment, templates, fixtures, and native validation tests exist on the active development branch, but the complete Ruff and package test gate has not yet been recorded as passing.

## Shared contract guarantee

Every adapter receives the same language-neutral API and template contract. An adapter may translate already-normalized facts into target spellings, but it must not:

- parse OpenAPI again;
- decode `x-codegen` dictionaries independently;
- infer resources, operation roles, dependencies, or schema relationships;
- weaken path, provider, collision, lifecycle, or write-policy safety;
- execute package managers or formatters automatically.

Templates retain the stable compatibility roots and typed normalized roots documented elsewhere. Raw source and extension data remain escape hatches rather than the preferred target-language API.

## Production adapter requirements

A new adapter is not complete when it is merely registered. It must include all of the following:

1. A canonical name and collision-free aliases.
2. Deterministic naming, reserved-word, file, package, and source-layout conventions.
3. Scalar, format, collection, map, nullable, reference, enum, request, response, and operation type mapping.
4. Target-specific imports derived from resolved virtual outputs.
5. At least one inspectable template pack that emits native source and package metadata.
6. Safe managed and immutable write roots.
7. First-run write and second-run cache-reuse tests.
8. Output uniqueness and physical-file assertions.
9. A native syntax, formatter, or compiler gate when the toolchain is installed.
10. Documentation of post-generation commands without executing them automatically.

## Current portable fixture

The five additional adapters share one OpenAPI fixture so parity is measurable. It includes:

- an object model;
- a referenced enum;
- a UUID-formatted field;
- an operation with a query parameter;
- an array response;
- raw OpenAPI and extension probes.

Each target emits:

```text
package manifest
native model
native enum
native operation client
contract variable probes
schema, operation, and resource probes
```

The fixture is generated twice. The first run must physically write every planned output; the second run must report cache reuse without rewriting managed files.

## Authoring another adapter

Keep the implementation layered:

```text
OpenAPI / JSONL
  -> language-neutral inference
  -> stable API and normalized contracts
  -> target adapter enrichment
  -> target templates
  -> path graph and writer
```

Add target conventions under `src/languages/`, register the adapter through the language decorator, provide a target import planner when source imports are meaningful, and add a reviewable fixture under `tests/fixtures/`. Do not add target-specific behavior to inference or the JSONL compiler.
