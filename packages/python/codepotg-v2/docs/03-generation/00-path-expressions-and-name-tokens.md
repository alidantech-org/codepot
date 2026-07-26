# Selection folders, path expressions, and name tokens

## Core rule

The pack filesystem is the default output program.

Literal folders and files preserve their relative location below `templates/`. Only a whole folder segment written as `{selectionKey}` is replaced through the pack manifest.

Example:

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

The final `.jinja` engine suffix is removed. The `.ts` target suffix remains. No semantic `entity.fileName` property is involved.

## Path syntax

CodepotG v2 uses three simple forms:

```text
{selectionKey}   registered selection folder
(expression)     bounded typed path/name expression
((value))        literal parenthesized value: (value)
```

Square brackets are ordinary literal characters.

Examples:

```text
{models}/(model.name.kebab.s).model.ts.jinja
{resourceFiles}/(resource.name.path.o)/index.ts.jinja
app/[id]/page.tsx.jinja
app/[...slug]/page.tsx.jinja
app/[[...slug]]/page.tsx.jinja
app/((admin))/page.tsx.jinja
```

The last example emits `app/(admin)/page.tsx`.

## Selection folders

A selection folder is a whole source-path segment:

```text
{repositories}
```

It must match a key under `CodepotgPack.yaml` `selections`:

```yaml
selections:
  repositories:
    paths: [src, repositories]
    select: entities.each
```

The selection key has two responsibilities:

1. contribute pack-relative output path segments through `paths`;
2. optionally establish a fixed data selection through `select`.

The folder name itself is not emitted.

Unknown selection keys are errors.

## `{root}`

`{root}` is built in and contributes no path segments.

```text
templates/{root}/package.json.jinja
```

emits:

```text
package.json
```

relative to the configured pack-instance output root.

It is useful when a pack author wants to group root-emitted files physically without adding that grouping folder to output.

## Literal paths

Literal source paths remain literal:

```text
templates/assets/logo.png          -> assets/logo.png
templates/src/config.ts.jinja      -> src/config.ts
templates/package.json.jinja       -> package.json
```

Literal static and binary files are copied unchanged. Literal templates are rendered and lose only the recognized engine suffix.

## Dynamic expressions

Dynamic values use one expression syntax:

```text
(entity.name.kebab.s)
(resource.name.path.o)
(option.clientName)
(project.name.snake.o)
```

The expression language is bounded and typed. It is not Jinja, Python, JavaScript, shell, or arbitrary object traversal.

Expressions may appear as a whole segment or as part of a filename:

```text
(entity.name.kebab.s).repository.ts.jinja
(resource.name.kebab.p)-routes.ts.jinja
```

A multi-segment `PathSegments` value may expand only when the expression occupies the whole path segment. It cannot be embedded inside a filename.

## Literal parentheses

Because single parentheses mark an expression, double parentheses escape literal parentheses:

```text
((admin)) -> (admin)
((group-name)) -> (group-name)
```

The parser checks the escaped form before expression parsing.

## Name token contract

Every neutral semantic item with a meaningful authored name exposes a typed `name` value.

Stable case projections:

```text
raw
clean
snake
kebab
camel
pascal
screaming
constant
dot
path
lower
upper
```

Every case projection exposes:

```text
o / original
s / singular
p / plural
number
```

Long names are also supported:

```text
original
singular
plural
```

Examples:

```text
(entity.name.pascal.s)
(entity.name.kebab.p)
(resource.name.path.o)
(operation.name.camel.o)
(enum.name.screaming.s)
```

`original` preserves source lexical number. `singular` and `plural` are deterministic, behavior-versioned inflections. Irregular and uncountable names are explicitly tested. Naming/inflection behavior participates in lock and cache identity.

## Stable expression roots

The initial registry supports typed descriptors for:

- current fixed-selection contexts such as `resource`, `entity`, `operation`, `schema`, `model`, `dto`, and `enum`;
- `project` identity and declared project values;
- `pack` identity/version;
- named semantic `source` metadata;
- `option` values declared by the pack;
- path-safe `binding` values;
- deterministic group/scope keys;
- already planned artifacts where the dependency graph permits them;
- target metadata registered by adapters.

Plugins may register additional namespaced typed values. Packs cannot register executable expression code.

## Expression safety

The compiler rejects:

- method calls;
- arbitrary indexing;
- unregistered properties;
- parser/source implementation objects;
- undeclared environment access;
- filesystem reads;
- non-deterministic values;
- unsafe path values;
- hidden joining/stringification of collections.

Diagnostics identify the source path, token span, unknown property, and available alternatives.

## Source path to destination algorithm

For each discovered file:

1. determine its path relative to `templates/`;
2. apply pack `.gitignore`, `include`, and `exclude` discovery rules;
3. classify `_partials` as non-emitting;
4. parse literal segments, `{selectionKey}` folders, `(expression)` values, and `((literal))` escapes;
5. establish fixed selection contexts for encountered selection folders;
6. replace each selection folder with its `paths` segments;
7. resolve typed expressions;
8. preserve literal prefixes, suffixes, and target extensions;
9. remove only a recognized template-engine suffix;
10. copy static/binary bytes unchanged;
11. normalize and validate all path segments;
12. prepend the project pack-instance output root;
13. reject traversal, absolute paths, reserved segments, case collisions, and duplicate destinations.

## Selection scope and nesting

Selection folders are evaluated left to right. A later fixed selector may use a context established by an earlier selection folder.

```text
{resources}/{resourceEntities}/(entity.name.kebab.s).entity.ts.jinja
```

could use:

```yaml
selections:
  resources:
    paths: [src, modules, (resource.name.path.o)]
    select: resources.each

  resourceEntities:
    paths: [entities]
    select: resource.entities.each
```

The output path is still relative to the pack-instance output root.

Aliases are normally inferred by the fixed selector. An optional inline alias may be used:

```yaml
select: resource.entities.each(repositoryEntity)
```

Aliases may not shadow active contexts silently.

## Imports and exports use planned paths

A selection's `imports` and `exports` refer to other selection keys. The planner resolves those dependencies after destinations and symbols are known.

```yaml
repositories:
  paths: [src, repositories]
  select: entities.each
  imports:
    entities: entities

repositoriesIndex:
  paths: [src, repositories]
  exports: [repositories]
```

Language adapters calculate legal module paths from the planned destinations. They do not choose output folders or parse pack source paths.

## Static files and `.gitignore`

Static and binary files are emitted without registration.

A pack-root `.gitignore` is a discovery control file and is not emitted. A generated `.gitignore` is authored as a template:

```text
templates/.gitignore.jinja -> .gitignore
```

This avoids accidentally copying the pack's own ignore rules into generated projects.

## Adapter responsibilities

Core owns:

- selection-folder parsing;
- fixed selector resolution;
- semantic name projections and inflection;
- typed expression evaluation;
- safe path composition;
- collision detection.

A language adapter owns:

- target suffix registration;
- final target filename validation;
- module path calculation;
- target imports/exports;
- reserved-name restrictions.

A template-engine adapter renders already planned output and cannot add destinations.

## Required tests

The path subsystem must test:

- every case and original/singular/plural projection;
- irregular and uncountable names;
- `{selectionKey}` and `{root}` folders;
- fixed `.each`/`.all` selectors and optional aliases;
- nested resource/entity selection folders;
- `(expression)` parsing and `((literal))` escaping;
- literal Next.js bracket routes;
- literal/static/binary discovery;
- `_partials` exclusion;
- pack `.gitignore`, include, and exclude rules;
- `.gitignore.jinja` emission;
- engine suffix stripping and target suffix preservation;
- invalid roots/properties with suggestions;
- traversal, reserved names, cycles, shadowing, and collisions;
- imports/exports consuming planned paths;
- rejection of invented `fileName`, `filePath`, and `directory` properties.
