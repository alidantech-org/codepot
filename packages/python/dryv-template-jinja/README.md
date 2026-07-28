# dryv-template-jinja

`dryv-template-jinja` is the independently installable, sandboxed Jinja adapter for Dryv. It implements the public `dryv.ports.TemplateEngine` protocol and renders only the source, immutable prepared context, and declared in-memory partials supplied in a `RenderRequest`.

## Supported now

- strict deterministic Jinja rendering with `StrictUndefined`;
- `SandboxedEnvironment` with no default globals and an audited filter/test set;
- immutable snapshots of safe scalars, tuples, sorted tuple-pair mappings, public Dryv frozen IR values, and approved enums;
- static includes, inheritance, imports, and from-imports through declared in-memory partials;
- dependency-cycle, depth, AST, context, template, partial, and streamed-output limits;
- cooperative cancellation with stable `JINJA_CANCELLED` diagnostics;
- structured source-aware diagnostics;
- instance-owned, thread-safe, bounded compilation caching;
- Python entry-point discovery through `dryv.template_engines`.

Recognized suffixes are `.j2`, `.jinja`, and `.jinja2`.

## Security boundary

The default engine has no filesystem loader, package loader, network client, environment-variable reader, process runner, writer, command executor, target renderer, output-path planner, or process-global Jinja environment/cache. Dynamic template dependencies are rejected. Context callables and arbitrary Python objects are rejected before compilation.

Loop metadata such as `loop.index`, `loop.first`, and `loop.last` is readable. Callable loop helpers, including `loop.cycle()` and `loop.changed()`, deliberately remain unavailable in the strict first-version profile because the callable policy permits only template-owned macros/block references and explicitly registered host helpers.

Autoescape is disabled because Dryv templates author arbitrary target files rather than an assumed HTML document.

## Construction

```python
from dryv_template_jinja import JinjaEngineRules, JinjaTemplateEngine

engine = JinjaTemplateEngine(rules=JinjaEngineRules(max_render_bytes=1_000_000))
```

The entry-point factory uses strict safe defaults:

```python
from dryv_template_jinja.plugin import create_plugin

engine = create_plugin()
```

Rules are host-controlled constructor values. They are never read from template context, environment variables, the working directory, YAML, or hidden global configuration.

## Approved defaults

Filters: `default`, `indent`, `join`, `length`, `lower`, `replace`, `sort`, `trim`, `unique`, `upper`.

Tests: `boolean`, `defined`, `equalto`, `float`, `integer`, `mapping`, `none`, `number`, `sequence`, `string`, `undefined`.

Globals: none.

## Deliberately blocked public integrations

- Named outputs require a public planner-declared named-output request/result contract.
- Target-compatible partial roles require public planner/template-registry metadata.
- Runtime cache-port integration requires a published cache contract suitable for compiled engine objects.
- Project/pack rule decoding requires the public configuration integration contract.

The adapter does not hide these values in `RenderRequest.context` and does not import private core modules to emulate them.