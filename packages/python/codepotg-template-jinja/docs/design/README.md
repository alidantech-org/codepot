# Jinja engine design reference

## Role

This package renders Jinja templates from planner-prepared immutable contexts. It never selects files, calculates outputs, resolves target-language imports independently, writes files, or executes commands.

## Planned plugin entry point

```toml
[project.entry-points."codepotg.template_engines"]
jinja = "codepotg_template_jinja.plugin:create_plugin"
```

## Pack rules example

```yaml
templateEngines:
  jinja:
    undefinedBehavior: error
    whitespace:
      trimBlocks: true
      leftStripBlocks: true
      keepTrailingNewline: true
    includes:
      dynamic: false
      maxDepth: 32
    sandbox:
      attributeAccess: restricted
      callableAccess: registeredOnly
    limits:
      maxRenderBytes: 5000000
```

Security-sensitive rules are host-only. A downloaded pack cannot enable Python imports, builtins, arbitrary attribute access, filesystem, environment, network, or process execution.

## Render context

The engine receives only immutable plain values and narrow registered helpers:

```text
selected semantic data
project/pack public values
effective target rules
resolved bindings/imports/exports
planned output metadata
registered pure helpers
```

It never receives runtime, writer, command executor, filesystem, pack provider, secret store, or environment objects.

## Includes

Includes resolve through the pack template registry. The planner validates dependencies, role, target compatibility, cycles, and depth before rendering.

A target-neutral partial may be shared. A TypeScript template cannot include a Dart partial.

## Named outputs

Named output blocks are allowed only when the manifest predeclares every output. The engine maps block IDs to planner-owned outputs; templates cannot choose paths.

## Cache

Compiled cache identity includes engine behavior version, rules, template digest, include digests, and helper/filter versions. Cache state is runtime/session scoped through a port, never a module-global dictionary.

See `../tasks/00-package-plan.md` and the core template-engine contract.
