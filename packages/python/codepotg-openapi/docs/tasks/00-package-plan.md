# OpenAPI adapter tasks

## Foundation

- [ ] Add isolated `pyproject.toml`, typed package metadata, entry point, and public dependency bounds.
- [ ] Add package import, entry-point discovery, and architecture tests.
- [ ] Implement immutable typed adapter options and capability metadata.

## Loading and validation

- [ ] Support YAML and JSON documents with exact source locations.
- [ ] Define local-file, in-memory, and explicitly authorized remote reference loaders.
- [ ] Validate document version, structure, duplicate names, operations, schemas, and references.
- [ ] Return typed diagnostics rather than parser-specific exceptions.

## Reference resolution

- [ ] Resolve local and external references once with cycle and recursion safeguards.
- [ ] Preserve original reference provenance and canonical identity.
- [ ] Prevent filesystem escapes and unauthorized network access.

## Neutral normalization

- [ ] Normalize documents, schemas, types, properties, enums, requests, responses, parameters, operations, tags, and security into neutral IR.
- [ ] Preserve required versus optional and nullable semantics without target-language assumptions.
- [ ] Avoid compatibility graphs and duplicate intermediate models.
- [ ] Prove deterministic ordering and immutable output.

## Quality and release

- [ ] Pass the shared source-adapter conformance suite.
- [ ] Add small unit fixtures plus realistic large OpenAPI integration fixtures.
- [ ] Add performance and memory regression tests for parse-once behavior.
- [ ] Document unsupported or ambiguous OpenAPI features with diagnostics.
- [ ] Version and publish independently from core.
