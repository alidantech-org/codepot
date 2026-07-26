# Fixed selections, selection folders, imports, barrels, and static files

## Selection is pack-owned

The project chooses a pack and its semantic input. The pack decides which fixed normalized records drive each registered emission selection.

The project never lists internal template files or selection rules.

## Fixed selection registry

Packs use documented selectors rather than arbitrary `from`/`as` definitions.

Initial examples:

```text
resources.each
resources.all
entities.each
entities.all
schemas.models.each
schemas.models.all
schemas.dtos.each
schemas.dtos.all
schemas.enums.each
schemas.enums.all
operations.each
operations.all
resource.entities.each
resource.operations.each
```

`.each` creates one context per item. `.all` creates one context containing the collection.

Default context names are inferred from the selector. Optional aliases are inline:

```yaml
select: entities.each(repositoryEntity)
```

## One selection registry

```yaml
selections:
  repositories:
    paths: [src, repositories]
    select: entities.each
    imports:
      entities: entities
    bindings: [baseRepository]
    symbols: [(entity.name.pascal.s)Repository]
```

The key `repositories` is both:

- the manifest identity of the emission group;
- the folder key used by `templates/{repositories}/`;
- the dependency key referenced by `imports` or `exports`.

No secondary selection aliases, root `paths`, exact `files`, or artifact namespaces are needed.

## Selection folders

```text
templates/{repositories}/(entity.name.kebab.s).repository.ts.jinja
```

`{repositories}` is replaced by:

```yaml
paths: [src, repositories]
```

The file repeats according to:

```yaml
select: entities.each
```

Every included descendant under the selection folder inherits the same selection context and output prefix.

## Nested selection folders

```yaml
selections:
  resources:
    paths: [src, modules, (resource.name.path.o)]
    select: resources.each

  resourceEntities:
    paths: [entities]
    select: resource.entities.each
```

```text
templates/{resources}/{resourceEntities}/(entity.name.kebab.s).entity.ts.jinja
```

Selection folders are resolved left to right, so `resourceEntities` may use the active `resource` context.

## Pack-root emission

`{root}` is built in:

```text
templates/{root}/package.json.jinja -> package.json
```

It allows physical grouping without an output folder.

## Imports are explicit

```yaml
repositories:
  paths: [src, repositories]
  select: entities.each
  imports:
    entities: entities
```

The mapping is `localName: selectionKey`.

The import resolver:

- accepts only declared selection providers;
- matches required semantic dependencies to explicit symbols;
- imports only the least required symbols;
- respects `.each`, `.all`, global, and parent scopes;
- rejects missing, ambiguous, duplicate, and conflicting providers;
- supplies a language-neutral plan to the language adapter/template.

A direct `.each` provider may produce several module imports. A global, `.all`, or barrel provider may produce one module import. The referenced selection determines the shape; no `outputs.*` namespace is used.

## Barrels and exports

A barrel is a normal template whose selection declares ordered exports:

```yaml
repositoriesIndex:
  paths: [src, repositories]
  exports: [repositories]
```

```text
templates/{repositoriesIndex}/index.ts.jinja
```

The template receives `exports.repositories`, including emitted paths and declared symbols. It controls whether to write wildcard, explicit, or type-only exports.

A barrel may export another barrel:

```yaml
rootIndex:
  paths: [src]
  exports: [entitiesIndex, repositoriesIndex]
```

Missing keys and export cycles are rejected before rendering.

## Aggregate templates

A template that selects a complete semantic collection uses `.all`:

```yaml
schemaRegistry:
  paths: [src]
  select: schemas.all
  symbols: [SchemaRegistry]
```

A template that aggregates emitted files uses `exports` instead. Semantic collections and emitted artifacts are not conflated.

## Literal, static, and binary content

Content outside a selection folder follows its literal relative path.

```text
templates/README.md.jinja -> README.md
templates/assets/logo.png -> assets/logo.png
```

Inside a selection folder, literal/static descendants repeat with that selection:

```text
templates/{resources}/README.md
templates/{resources}/assets/icon.png
```

Bytes remain unchanged for static/binary files.

## Ignore behavior

Discovery respects:

- the pack-root `.gitignore`;
- manifest `include` patterns;
- manifest `exclude` patterns;
- `_partials/**` as non-emitting content.

The pack's control `.gitignore` is never copied. To generate one, author:

```text
templates/.gitignore.jinja
```

## Ordering

- fixed semantic collections provide deterministic order;
- `exports` preserves the declared selection-key order;
- individual emissions use deterministic path/scope order;
- templates may further control textual ordering using the supplied descriptors.

## Required tests

- fixed `.each` and `.all` selectors;
- optional aliases;
- selection-folder fan-out and nested parent scope;
- `{root}`;
- explicit imports and least-required symbols;
- direct versus barrel imports;
- barrels exporting barrels;
- aggregate semantic templates versus emitted-file barrels;
- static/binary fan-out;
- ignore/include/exclude behavior;
- deterministic ordering;
- unknown keys, missing imports, symbol conflicts, cycles, traversal, and collisions.
