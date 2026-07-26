# Template and pack file model

## Files are discovered, not registered

Every included file below the default `templates/` root becomes one immutable source descriptor.

The pack manifest does not repeat a `files` registry or assign roles to ordinary files.

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
templates/{repositories}/(entity.name.kebab.s).repository.ts.jinja
```

with:

```yaml
selections:
  repositories:
    paths: [src, repositories]
    select: entities.each
```

may emit:

```text
src/repositories/order.repository.ts
```

## File kinds are inferred

### Template

A file with a recognized template-engine suffix. The engine suffix is removed after planning.

```text
user.entity.ts.jinja -> user.entity.ts
```

The remaining suffix selects the target adapter when registered.

### Static text or binary

A non-template file is copied unchanged.

### Partial

Anything below `templates/_partials/` is available to the template engine and is not emitted.

### Authored barrel

A barrel is an ordinary template located under a selection folder whose manifest entry declares `exports`.

```yaml
repositoriesIndex:
  paths: [src, repositories]
  exports: [repositories]
```

The template receives planned emitted paths and symbols and writes its own target-language export text.

### Generated `.gitignore`

A pack-root `.gitignore` controls discovery and is not emitted. To generate one:

```text
templates/.gitignore.jinja -> .gitignore
```

## Target and engine inference

For:

```text
user.entity.ts.jinja
```

- `.jinja` selects the engine;
- `.ts` selects the target adapter;
- `.jinja` is removed;
- `.ts` remains.

Longest-known suffix matching resolves compound extensions. Ambiguous files such as `Dockerfile.jinja` may use adapter-supported explicit metadata only when the filesystem cannot identify the target.

## Selection-backed files

Only a folder segment in `{selectionKey}` form requires manifest registration:

```text
templates/{models}/(model.name.kebab.s).model.ts.jinja
```

```yaml
selections:
  models:
    paths: [src, models]
    select: schemas.models.each
    symbols: [(model.name.pascal.s)]
```

The selection entry applies to every included descendant under that folder. Literal descendants keep their relative structure.

## Generated dependencies

A selection declares generated dependencies explicitly:

```yaml
repositories:
  paths: [src, repositories]
  select: entities.each
  imports:
    entities: entities
```

The resolver matches only required declared symbols and supplies an immutable import plan to the language adapter/template.

No template may discover other generated files by scanning the filesystem.

## Symbols

Selections declare generated symbols before rendering:

```yaml
symbols: [(entity.name.pascal.s)Repository]
```

CodepotG never parses rendered source to guess exports.

## Multiple physical templates per selection

A selection folder may contain several templates and static files:

```text
templates/{repositories}/
├── (entity.name.kebab.s).repository.ts.jinja
├── (entity.name.kebab.s).repository.spec.ts.jinja
└── metadata.json
```

All inherit the same selection context and destination prefix. Separate file registration is unnecessary.

Profile-specific activation is deferred until a concrete pack requirement proves a compact filesystem or selection-level design; the removed `filePatterns`/`files` profile mechanism is not part of the approved baseline.

## Duplicate destination policy

Any two planned emissions targeting the same normalized destination are an error. Last-write-wins is prohibited.

## Required tests

- deterministic discovery and ignore behavior;
- one source descriptor per included file;
- engine/target inference;
- literal output derivation;
- selection-folder fan-out;
- dynamic name expressions and escaped parentheses;
- static/binary copying;
- partial exclusion;
- authored barrel contexts;
- explicit generated imports and symbols;
- `.gitignore` control versus `.gitignore.jinja` output;
- duplicate destination rejection;
- rejection of semantic `fileName`, `filePath`, and `directory` conveniences.
