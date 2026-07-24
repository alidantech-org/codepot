# CodepotG Template Authoring Documentation

This documentation defines the public authoring surface for CodepotG Jinja template packs.
It describes the information that templates can consume, how that information is normalized,
and how template packs can remain independent of OpenAPI parsing and language-specific internals.

CodepotG keeps its established pipeline:

```text
OpenAPI document
  -> inference
  -> language-neutral API contract
  -> template contract
  -> language adapter
  -> Jinja template pack
  -> emitted files
```

The planned contract expansion is additive. Existing template variables, bundled template packs,
configuration behavior, inference boundaries, language adapters, path planning, import planning,
and emission behavior remain supported.

## Guides

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
2. Templates do not parse `$ref` strings, merge inheritance, infer operation roles, or decode
   extension dictionaries.
3. Known OpenAPI and `x-codegen` information is exposed through named variables.
4. Original references and source objects remain available as lossless escape hatches.
5. Unknown extensions are preserved and reported; they are not silently discarded.
6. Missing optional information becomes a safe empty object, tuple, or explicit unset value.
7. Language-specific rendering belongs to language adapters and template packs.
8. Every documented variable is treated as public API.

## Stability levels

The documentation uses these terms:

- **Stable**: supported public template API; additions are allowed, incompatible changes are not.
- **Compatibility alias**: an existing path retained while templates migrate to a normalized path.
- **Derived**: calculated once by CodepotG from normalized facts and exposed for convenience.
- **Raw escape hatch**: original source data retained for forward compatibility; not the preferred
  authoring interface.
- **Extension data**: unknown or project-specific `x-*` information preserved by key.

## Intended audience

These guides are for template-pack authors. They deliberately avoid Python implementation examples.
Examples use Jinja expressions, `paths.yaml`, variable trees, and generated-output concepts only.
