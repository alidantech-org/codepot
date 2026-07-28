# Jinja adapter contract and security model

## Public boundary

`dryv-template-jinja` implements only `dryv.ports.TemplateEngine`. A render request supplies one root template ID and source, one sorted immutable context, and one sorted in-memory partial registry. A result supplies either one text value or structured diagnostics.

The adapter does not normalize sources, select templates, infer targets, plan paths, write files, execute commands, inspect projects, discover packs, or return named outputs.

## Rules and limits

`JinjaEngineRules` is frozen and host-controlled. The entry-point factory uses these defaults:

| Rule | Default |
|---|---:|
| `trim_blocks` | `True` |
| `lstrip_blocks` | `True` |
| `keep_trailing_newline` | `True` |
| `newline_sequence` | `"\n"` |
| `max_template_id_length` | 512 bytes |
| `max_template_bytes` | 1,000,000 bytes |
| `max_partial_count` | 1,000 |
| `max_partial_bytes` | 5,000,000 bytes |
| `max_context_depth` | 64 |
| `max_context_items` | 100,000 |
| `max_include_depth` | 32 |
| `max_render_bytes` | 5,000,000 bytes |
| `max_ast_nodes` | 100,000 |
| `cache_entries` | 256 |

Rules are never decoded from context, environment variables, the working directory, hidden files, or mutable global configuration.

## Context model

Accepted values are `None`, booleans, finite integers/floats, UTF-8 strings, tuples of accepted values, sorted tuple-pair mappings, approved public frozen Dryv semantic dataclasses/enums, and immutable helper descriptors. Values are converted to request-local immutable snapshots before Jinja sees them.

Public dataclass fields are copied. Private fields are omitted. `Name` and `NameProjection` expose only the documented case and number projections. A fresh `Name` clone is used while reading cached projections so the caller's object is not mutated.

Classes, modules, arbitrary dataclasses/enums, callables, paths, file handles, sockets, subprocess objects, environments, registries, runtimes, writers, loaders, resolvers, and caches are rejected.

## Sandbox

The engine uses `jinja2.sandbox.SandboxedEnvironment`, `StrictUndefined`, no autoescape, no default globals, and a registry cleared before audited helpers are installed.

Approved filters: `default`, `indent`, `join`, `length`, `lower`, `replace`, `sort`, `trim`, `unique`, `upper`.

Approved tests: `boolean`, `defined`, `equalto`, `float`, `integer`, `mapping`, `none`, `number`, `sequence`, `string`, `undefined`.

Approved default globals: none.

Attribute access is limited to public keys of immutable snapshots plus the narrow Jinja runtime attributes required for loops and imported macros. Every private or dunder attribute is denied. Calls are limited to template-owned macros/block references and explicitly registered immutable host helper wrappers. Context callables are rejected before rendering.

Loop metadata such as `loop.index`, `loop.first`, and `loop.last` is readable. `loop.cycle()` and `loop.changed()` deliberately remain denied in the strict first-version profile because they are callable `LoopContext` methods and are not template-owned macros, block references, or registered host helpers. Supporting them later requires a separate audited callable-policy change and behavior-version review.

## Declared dependencies

Only one static string is accepted by `include`, `extends`, `import`, and `from ... import`. Every dependency must exist in `request.partials`, use a normalized relative POSIX registry ID, remain within the include-depth limit, and participate in a cycle-free graph. Dynamic expressions, fallback lists, traversal IDs, and `ignore missing` are rejected before compilation.

Only reachable partial IDs and source digests enter the compilation identity. Unused partials do not invalidate a compiled root.

## Cache and cancellation

The compilation cache is instance-owned, bounded, lock-protected, deterministic, and explicitly clearable. Its identity includes package and behavior versions, all rules, the Jinja version, helper descriptors, the root ID/source digest, and reachable partial IDs/source digests. It stores compiled templates only, never request contexts, secrets, runtime sessions, paths, clients, or writers.

Cancellation is cooperative. Checks run before and after context preparation, around dependency parsing and compilation, for every generated output chunk, and before success. Cancellation returns `JINJA_CANCELLED` with no partial content and does not disclose the cancellation reason.

## Diagnostics

Stable error codes are:

- `JINJA_RULE_INVALID`
- `JINJA_TEMPLATE_ID_INVALID`
- `JINJA_TEMPLATE_INVALID`
- `JINJA_TEMPLATE_TOO_LARGE`
- `JINJA_PARTIAL_INVALID`
- `JINJA_CONTEXT_UNSAFE`
- `JINJA_CONTEXT_LIMIT`
- `JINJA_SYNTAX`
- `JINJA_UNDEFINED`
- `JINJA_INCLUDE_DYNAMIC`
- `JINJA_INCLUDE_MISSING`
- `JINJA_INCLUDE_CYCLE`
- `JINJA_INCLUDE_DEPTH`
- `JINJA_ATTRIBUTE_DENIED`
- `JINJA_CALLABLE_DENIED`
- `JINJA_HELPER_CONFLICT`
- `JINJA_RENDER_LIMIT`
- `JINJA_CANCELLED`
- `JINJA_RUNTIME`

`JINJA_TEMPLATE_INVALID` is reserved for malformed root source values. Partial source failures continue to use `JINJA_PARTIAL_INVALID`.

Template locations use `SourceKind.TEMPLATE`, one-based lines, and column 1 only when a reliable Jinja line is available. Details are sorted and exclude paths, memory addresses, secrets, traceback text, and unstable exception messages.

## Blocked public integrations

- Named outputs: a public planner-declared named-output request/result contract is required.
- Target-compatible template registry metadata: planner/registry roles and target compatibility are not present in `RenderRequest`.
- Runtime cache integration: no public compiled-template cache port exists.
- Project/pack rule decoding: no public engine-configuration integration contract exists.

These capabilities are not hidden inside context and are not emulated through private core imports.