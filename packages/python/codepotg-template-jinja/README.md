# codepotg-template-jinja

Installable sandboxed Jinja template-engine adapter for CodepotG v2.

This package renders immutable plain template contexts and resolves includes through the typed pack template registry. It must not receive rich filesystem, resolver, source-document, application, or command objects.

## Planned entry point

```toml
[project.entry-points."codepotg.template_engines"]
jinja = "codepotg_template_jinja.plugin:create_plugin"
```

## Responsibilities

- deterministic sandboxed rendering;
- strict undefined values and typed whitespace/include rules;
- explicit approved filters and immutable contexts;
- declared template and neutral-fragment includes;
- dependency reporting, diagnostics, cancellation, and scoped caches.

See [`docs/tasks/00-package-plan.md`](docs/tasks/00-package-plan.md).
