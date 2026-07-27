# Author compiler and validation

## Compiler phases

1. Resolve and validate author options.
2. Collect explicit declarations without compilation side effects.
3. Freeze the author session.
4. Validate Pydantic/author declaration models.
5. Assign deterministic declaration and semantic identities.
6. Build per-kind ref indexes.
7. Resolve aliases, forward refs, and typed cross-references.
8. Compile reusable properties, primitives, aliases, enums, and object schemas.
9. Expand schema projections and derivations.
10. Compile supported field capabilities and references.
11. Compile storage mappings.
12. Compile policies and access declarations.
13. Compile events and effects.
14. Compile operations, schema uses, failures, and known facets.
15. Compile value sources when supported by core.
16. Compile views and parts.
17. Compile presentations when supported by core.
18. Compile workflows, steps, transitions, waits, decisions, and compensation.
19. Construct immutable core groups and contract.
20. Run `codepotg.ir.validate_contract`.
21. Canonicalize, calculate digest, and build `AuthoringResult`.
22. Optionally serialize canonical JSON/YAML.

## Pass rules

- Each declaration compiles exactly once.
- Each ref resolves through one session-scoped linker.
- Pass ordering is explicit and tested.
- No process-global cache or registry exists.
- Stable IDs never depend on object identity, timestamps, random UUIDs, temporary paths, or dictionary insertion accidents.
- Unsupported core concepts produce exact diagnostics and do not partially enter the contract.

## Result

```python
@dataclass(frozen=True, slots=True)
class AuthoringResult:
    contract: Contract | None
    diagnostics: Diagnostics
    digest: str
```

Expected invalid authoring returns diagnostics. Raw Pydantic errors, parser errors, and ordinary linker exceptions must be converted into stable author diagnostics.

## Diagnostic families

```text
AUTHOR_OPTION_*
AUTHOR_DECLARATION_*
AUTHOR_DUPLICATE_*
AUTHOR_REF_*
AUTHOR_PROPERTY_*
AUTHOR_SCHEMA_*
AUTHOR_FIELD_*
AUTHOR_STORAGE_*
AUTHOR_POLICY_*
AUTHOR_EVENT_*
AUTHOR_OPERATION_*
AUTHOR_FACET_*
AUTHOR_SOURCE_*
AUTHOR_VIEW_*
AUTHOR_PRESENTATION_*
AUTHOR_WORKFLOW_*
AUTHOR_TRANSPORT_*
AUTHOR_CORE_UNSUPPORTED
AUTHOR_LIMIT_*
```

Diagnostics include the authoring module/file/span where available, declaration path, expected kind, actual kind, target identity, and stable sorted details.

## Digest

The digest includes:

- author package and behavior versions;
- core/IR/API versions;
- canonical compiled semantic content;
- all author options affecting output;
- Pydantic interpretation behavior version;
- projection/derivation behavior version;
- canonical tag/guidance behavior when supported;
- transport schema version when serializing.

Formatting-only JSON/YAML differences do not alter semantic digest.
