# OpenAPI adapter support matrix

This document describes `codepotg-openapi` `2.0.0a2`. Source support is intentionally narrower than the full OpenAPI specification and narrower than the planned OA-001..OA-020 roadmap.

## Implemented

### Public adapter contract

- `from codepotg_openapi import OpenApiSourceAdapter`
- `codepotg_openapi.create_plugin()`
- `codepotg.source_adapters/openapi` entry-point discovery
- immutable `SourceAdapterResult`
- composed cancellation handling
- core-owned final `validate_contract()` validation
- deterministic digest over semantic inputs, behavior options, versions, and reference authority

### Loading and parsing

- in-memory UTF-8 JSON or YAML
- absolute local root files
- local references contained beneath the authorized root
- host-injected controlled external references
- duplicate JSON/YAML key rejection
- JSON Pointer resolution, cycles, document limits, and reference-depth limits
- one canonical external load per normalization session
- no external-byte cache shared across normalization sessions
- YAML conversion depth, expanded-node, alias-expansion, and recursive-alias limits

### Standard OpenAPI normalization

- OpenAPI `3.0.x` and `3.1.x` structural roots
- tag-owned groups without cloning multi-tag operations
- component and inline structural schemas
- primitive, literal, enum, object, array, map, tuple, union, intersection, alias, and unknown schema forms where the current public kernel can represent them
- required, nullable, read-only, and supported field constraints
- HTTP operations with stable operation identities
- parameters and request-body schema uses
- distinct successful outputs and declared failures
- minimum `HttpFacet(method, path, operation_id)`
- bounded provenance, raw values, and optional unknown extensions

## Preserved with diagnostics because the current public kernel is narrower

- parameter transport binding details beyond neutral inputs
- request and response media types
- response status/header/link details beyond output/failure records
- operation-level server overrides
- `writeOnly`
- typed non-string enum literal identity
- schema roles such as `dto`

These facts remain bounded source metadata where possible. Preserving a fact does not add a new kernel field or facet.

## Not implemented

| Roadmap area | Status |
|---|---|
| OA-009 security/access normalization | Not implemented |
| OA-010 typed versioned `x-codegen` decoder | Not implemented |
| OA-011 storage mappings | Not implemented |
| OA-012 views and interaction triggers | Not implemented |
| OA-013 policies and access metadata | Not implemented |
| OA-014 events/listeners/effects | Not implemented |
| OA-015 execution hooks/workflows/compensation | Not implemented |
| OA-019 realistic fixture/legacy comparison benchmark | Not implemented |
| OA-020 performance benchmark publication | Not implemented |

When `x-codegen` exists, the default tolerant policy emits `OA_XCODEGEN_NOT_IMPLEMENTED` and ignores it. `strict` and `deny` return an error and no contract. The plugin does not advertise an `x-codegen` capability.

## Security boundary

The adapter never grants its own network authority. Request options can choose among host-authorized reference policies but cannot create loaders, add trusted hosts, or expand filesystem roots. Diagnostic messages redact URL user information and do not include source bytes or parser objects.
