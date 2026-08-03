# Architecture rules

## Governing flow

```text
Authoring
    ↓
Canonical Dryv Runtime IR
    ↓
Templating
    ↓
Usage and generated output
```

## Ownership

- Authoring defines software meaning and compiles it into Runtime IR.
- Authoring does not generate application source, select packs, define output paths, write generated files, or serialize IR.
- The runtime owns canonical meaning, validation, serialization, loading, inspection, planning, and safe generation orchestration.
- Runtime IR is the only semantic authority.
- Packs define how canonical meaning becomes artifacts. Packs do not redefine semantics.
- Templates own every emitted character.
- Target adapters provide target validation and path or module facts; they do not render target syntax.
- Usage connects authored source or serialized IR, packs, bindings, options, destinations, and commands.
- The CLI is a frontend over public runtime operations and contains no competing domain logic.

## Required properties

- Deterministic: equal locked inputs produce equal plans and artifacts.
- Explainable: selection, values, dependencies, paths, and ownership are inspectable.
- Portable: canonical meaning and pack contracts do not depend on hidden machine state.
- Safe: planning completes before writes; unmanaged and manually edited files are protected.
- Closed: plugins and packs cannot invent semantic objects, selectors, context roots, or validation rules.

## Architecture changes

Do not silently change these boundaries. Use the architecture-change skill and obtain explicit approval before implementation.
