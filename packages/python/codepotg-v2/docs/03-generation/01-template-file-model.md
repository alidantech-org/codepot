# Template and pack file model

## Files are discovered, not registered

Every included file below the default `templates/` root becomes one immutable source descriptor.

The pack manifest does not repeat a `files` registry, assign roles to ordinary files, or activate hidden profiles.

Discovery applies:

1. the pack-root `.gitignore`;
2. manifest `include` patterns;
3. manifest `exclude` patterns;
4. deterministic path ordering.

## Source path owns the default destination

Literal source paths preserve their relative structure:

```text
templates/package.json.jinja -> package.json
templates/src/config.ts.jinja -> src/config.ts
templates/assets/logo.png -> assets/logo.png
```

Selection folders and path expressions are resolved before the pack-instance output root is prepended:

```text
templates/{repositories}/(mapping.schema.name.kebab.s).repository.ts.jinja
```

with:

```yaml
selections:
  repositories:
    paths: [src, repositories]
    select: groups.storage.mappings.each
```

may emit:

```text
src/repositories/order.repository.ts
```

## File kinds are inferred

### Template

A file with a recognized template-engine suffix. The engine suffix is removed after planning:

```text
order.repository.ts.jinja -> order.repository.ts
```

The remaining suffix selects the target adapter when registered.

### Static text or binary

A non-template file is copied unchanged.

### Partial

Anything below `templates/_partials/` is available to the template engine and is not emitted.

### Authored barrel

A barrel is an ordinary template located under a selection folder whose manifest entry declares `exports`:

```yaml
repositoriesIndex:
  paths: [src, repositories]
  exports: [repositories]
```

The template receives planned emitted paths, module/path facts, semantic identities, and symbols and writes its own target-language export text.

### Generated `.gitignore`

A pack-root `.gitignore` controls discovery and is not emitted. To generate one:

```text
templates/.gitignore.jinja -> .gitignore
```

## Target and engine inference

For:

```text
order.repository.ts.jinja
```

- `.jinja` selects the engine;
- `.ts` selects the target adapter;
- `.jinja` is removed;
- `.ts` remains.

Longest-known suffix matching resolves compound extensions. Ambiguous files such as `Dockerfile.jinja` may use adapter-supported explicit target metadata only when the filesystem cannot identify the target.

Target adapters validate output names and calculate target-aware path/module facts. They do not render source syntax.

## Selection-backed files

Only a folder segment in `{selectionKey}` form requires manifest registration:

```text
templates/{schemaTypes}/(schema.name.kebab.s).ts.jinja
```

```yaml
selections:
  schemaTypes:
    paths: [src, types, schemas]
    select: groups.schemas.objects.each
    symbols:
      - (schema.name.pascal.s)
```

The selection entry applies to every included descendant under that folder. Literal descendants keep their relative structure.

Selectors use the fixed root-first registry. Packs cannot introduce `resource`, `model`, `entity`, frontend/UI, reversed-root, or arbitrary graph-query selectors.

## Generated dependencies

A selection declares generated dependencies explicitly:

```yaml
repositories:
  paths: [src, repositories]
  select: groups.storage.mappings.each
  imports:
    persistenceType: persistenceTypes
```

The resolver matches provider artifacts through semantic identity, active group scope, selection key, and declared symbols. It supplies immutable dependency and target-aware module/path descriptors under `imports.persistenceType`.

The template authors all syntax:

```jinja
{% for module in imports.persistenceType.modules %}
import { {{ module.symbols | join(", ") }} } from "{{ module.specifier }}";
{% endfor %}
```

No template may discover generated files by scanning the filesystem. No language adapter may inject the statement.

## Symbols

Selections declare generated symbols before rendering:

```yaml
symbols:
  - (mapping.schema.name.pascal.s)Repository
```

CodepotG never parses rendered source to guess exports.

## Multiple physical templates per selection

A selection folder may contain several templates and static files:

```text
templates/{repositories}/
├── (mapping.schema.name.kebab.s).repository.ts.jinja
├── (mapping.schema.name.kebab.s).repository.spec.ts.jinja
└── metadata.json
```

All inherit the same immutable `mapping` selection context and destination prefix. Separate file registration is unnecessary.

Materially different generated products use separate packs rather than hidden profile/file-ID activation. Pack options may vary authored template behavior only within one coherent deterministic file inventory.

## Template context ownership

Template contexts contain only documented closed-kernel and planning values:

```text
group
schema
operation
view
mapping
workflow
policy
event
imports
exports
options
bindings
artifact
target
```

Adapters and packs cannot add semantic context roots/properties. Unknown source metadata is accessible only through bounded documented raw/extension values where permitted.

## Duplicate destination policy

Any two planned emissions targeting the same normalized destination are an error. Last-write-wins is prohibited.

## Required tests

- deterministic discovery and ignore behavior;
- one source descriptor per included file;
- engine/target inference;
- literal output derivation;
- root-first selection-folder fan-out;
- rejection of removed/reversed/query selectors;
- dynamic name expressions and escaped parentheses;
- static/binary copying;
- partial exclusion;
- authored barrel contexts;
- explicit semantic generated dependencies and symbols;
- template-authored import/export syntax;
- `.gitignore` control versus `.gitignore.jinja` output;
- duplicate destination rejection;
- rejection of profiles, semantic extension, and semantic `fileName`, `filePath`, or `directory` conveniences.
