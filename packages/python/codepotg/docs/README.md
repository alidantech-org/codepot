# CodepotG Template Authoring Documentation

This documentation defines the public authoring surface for CodepotG Jinja template packs.
It describes the information that templates can consume, how that information is normalized,
and how template packs can remain independent of OpenAPI parsing and language-specific internals.

CodepotG supports two generation paths during migration:

```text
legacy folder packs
  OpenAPI -> compatibility inference -> full template contract -> Jinja

selection graph packs
  OpenAPI -> indexed JSONL -> bounded selection context -> dependency graph
          -> bounded render workers -> atomic writer
```

Existing template variables and folder packs remain supported while graph packs adopt bounded globals, explicit providers, barrels, and lazy JSONL source access.

## Guides

- [`paths.yaml` graph](paths-yaml.md) defines named selections, emissions, explicit dependency providers, barrels, bounded contexts, lazy source variables, graph scheduling, and legacy migration.
- [Bounded normalized roots](bounded-normalized-roots.md) lists the public graph-template roots for complete schema keywords, HTTP/domain facts, resource and operation runtime metadata, inherited entities, and authored frontends.
- [Realistic template fixtures](realistic-template-fixtures.md) separates nine-file smoke tests from the large-contract Nest, Next, and Dart generation and profiling gate.
- [Performance and memory tracing](performance-memory.md) explains the JSON/YAML memory paths, stage profiler, runtime trace variables, leak interpretation, and test fixture tiers.
- [Template authoring](template-authoring.md) explains template-pack composition, scopes,
  collections, contextual variables, naming, imports, path selection, and safe authoring rules.
- [Template variables](template-variables.md) is the fixed public variable reference for `project`,
  `api`, resources, schemas, operations, entities, access policies, frontends, language helpers,
  emission information, and contextual items.
- [Normalized contract architecture](normalized-contract.md) explains how loading, inference,
  language-neutral contracts, template contracts, adapters, and emission remain separate.
- [Normalized x-codegen metadata](x-codegen-metadata.md) explains how resources, query rules,
  cache behavior, access rules, runtime hooks, sources, entities, relations, constraints,
  frontends, UI metadata, and structured notes become predictable template variables.
- [Lossless OpenAPI access](openapi-preservation.md) defines how standard OpenAPI, JSON Schema,
  known Codepot extensions, unknown extensions, references, and original source objects are
  preserved without forcing templates to parse raw dictionaries.
- [Language adapters](language-adapters.md) explains how every target language and text format can
  consume the same normalized contract without adding target-specific behavior to inference.
- [Compatibility](compatibility.md) defines the non-breaking migration and stability policy.

## Public contract principles

1. Templates consume stable, normalized facts.
2. Templates do not parse `$ref` strings, merge inheritance, infer operation roles, or decode extension dictionaries.
3. Known OpenAPI and `x-codegen` information is exposed through named variables.
4. Original references and source objects remain available as lossless escape hatches.
5. Unknown extensions are preserved and reported; they are not silently discarded.
6. Missing optional information becomes a safe empty object, tuple, or explicit unset value.
7. Language-specific rendering belongs to language adapters and template packs.
8. Every documented variable is treated as public API.
9. Graph templates receive only bounded globals, their declared selection, provider facts, and lazy resolvers.
10. A generated dependency is valid only when an explicit configured provider actually emits its ref or symbol.
11. Performance evidence must identify the exact template pack and preserve generated output when human review is required.

## Stability levels

The documentation uses these terms:

- **Stable**: supported public template API; additions are allowed, incompatible changes are not.
- **Compatibility alias**: an existing path retained while templates migrate to a normalized path.
- **Derived**: calculated once by CodepotG from normalized facts and exposed for convenience.
- **Raw escape hatch**: original source data retained for forward compatibility; not the preferred authoring interface.
- **Extension data**: unknown or project-specific `x-*` information preserved by key.

## Intended audience

These guides are for template-pack authors. They deliberately avoid Python implementation examples.
Examples use Jinja expressions, `paths.yaml`, variable trees, and generated-output concepts only.
