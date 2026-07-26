# Selection folders, path expressions, and name tokens

## Core rule

The pack filesystem is the default output program.

Literal folders and files preserve their relative location below `templates/`. Only a whole folder segment written as `{selectionKey}` is replaced through the pack manifest.

Example:

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

The final `.jinja` engine suffix is removed. The `.ts` target suffix remains. No semantic `fileName` property is involved.

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
{schemas}/(schema.name.kebab.s).ts.jinja
{groupModules}/(group.name.path.o)/index.ts.jinja
{operations}/(operation.name.kebab.s).operation.ts.jinja
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
    select: groups.storage.mappings.each
```

The selection key:

1. contributes pack-relative output path segments through `paths`;
2. optionally establishes one fixed semantic selection through `select`.

The folder name itself is not emitted. Unknown selection keys are errors.

## `{root}`

`{root}` is built in and contributes no path segments:

```text
templates/{root}/package.json.jinja -> package.json
```

It groups root-emitted files physically without adding that grouping folder to output.

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
(group.name.path.original)
(schema.name.kebab.singular)
(operation.name.camel.original)
(mapping.schema.name.pascal.singular)
(workflow.name.kebab.original)
(option.clientName)
(project.name.snake.original)
```

The expression language is bounded and typed. It is not Jinja, Python, JavaScript, shell, or arbitrary object traversal.

Expressions may appear as a whole segment or as part of a filename:

```text
(schema.name.kebab.s).schema.ts.jinja
(operation.name.kebab.s)-handler.ts.jinja
```

A multi-segment path value may expand only when the expression occupies the whole path segment. It cannot be embedded inside a filename.

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

The ordering is always:

```text
x.name.{casing}.{number}
```

Examples:

```text
(group.name.path.original)
(schema.name.pascal.singular)
(operation.name.camel.original)
(field.name.snake.original)
(mapping.schema.name.kebab.singular)
(event.name.dot.original)
```

Do not introduce reversed forms such as:

```text
schema.name.singular.pascal
```

`original` preserves source lexical number. `singular` and `plural` are deterministic, behavior-versioned inflections. Irregular and uncountable names are explicitly tested. Naming/inflection behavior participates in lock and cache identity.

## Stable expression roots

Expression roots come only from the closed semantic kernel and the current planned invocation.

Initial semantic roots include:

```text
group
schema
field
operation
input
output
failure
view
mapping
workflow
step
policy
event
```

Other documented roots include:

```text
project
pack
source
option
binding
imports
exports
artifact
target
```

Semantic paths follow outer-to-inner order:

```text
group.operations
operation.facets.http
mapping.schema
workflow.steps
step.compensation.operation
```

Adapters and packs cannot register additional semantic roots or arbitrary expression properties. A new root/property requires a kernel change and behavior version.

The expression registry does not expose neutral roots named:

```text
resource
model
entity
frontend
ui
```

Those may appear only as literal template vocabulary, source provenance, or bounded raw/extension data.

## Expression safety

The compiler rejects:

- method calls;
- arbitrary indexing;
- unregistered roots or properties;
- arbitrary graph traversal;
- parser/source implementation objects;
- undeclared environment access;
- filesystem reads;
- non-deterministic values;
- unsafe path values;
- hidden joining/stringification of collections;
- semantic `fileName`, `filePath`, or `directory` shortcuts.

Diagnostics identify the source path, token span, unknown property, and available alternatives.

## Source path to destination algorithm

For each discovered file:

1. determine its path relative to `templates/`;
2. apply pack `.gitignore`, `include`, and `exclude` discovery rules;
3. classify `_partials` as non-emitting;
4. parse literal segments, `{selectionKey}` folders, `(expression)` values, and `((literal))` escapes;
5. establish fixed root-first selection contexts for encountered selection folders;
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
{groupModules}/{operations}/(operation.name.kebab.s).ts.jinja
```

may use:

```yaml
selections:
  groupModules:
    paths: [src, modules, (group.name.path.o)]
    select: groups.each

  operations:
    paths: [operations]
    select: group.operations.each
```

The output path remains relative to the pack-instance output root.

An optional inline alias may be used:

```yaml
select: group.operations.each(handlerOperation)
```

Aliases may not shadow active contexts silently.

The planner rejects reversed or ambiguous selector roots such as `operations.group`, `http.groups`, or `storage.groups`.

## Imports and exports use planned paths

A selection's `imports` and `exports` refer to other selection keys. The planner resolves semantic/provider matches after destinations and symbols are known.

```yaml
repositories:
  paths: [src, repositories]
  select: groups.storage.mappings.each
  imports:
    persistenceType: persistenceTypes

repositoriesIndex:
  paths: [src, repositories]
  exports: [repositories]
```

CodepotG calculates stable provider artifact identities and destination-relative path facts. A target adapter may validate/normalize target-aware module specifier facts. The template authors all import/export statements and formatting.

## Static files and `.gitignore`

Static and binary files are emitted without registration.

A pack-root `.gitignore` is a discovery control file and is not emitted. A generated `.gitignore` is authored as a template:

```text
templates/.gitignore.jinja -> .gitignore
```

## Responsibility boundaries

Core owns:

- closed semantic roots and properties;
- root-first fixed selector resolution;
- selection-folder parsing;
- semantic name projections and inflection;
- typed expression evaluation;
- safe path composition;
- provider/artifact path facts;
- collision detection.

A language adapter may own:

- target suffix registration;
- target filename and reserved-name validation;
- target-aware module/path normalization and validation;
- capability facts required by templates.

A language adapter does not emit imports, exports, types, literals, comments, validators, decorators, or framework syntax.

A template-engine adapter renders already planned output and cannot add destinations or semantic values.

## Required tests

The path subsystem must test:

- every case and original/singular/plural projection in the correct order;
- irregular and uncountable names;
- `{selectionKey}` and `{root}` folders;
- root-first fixed `.each`/`.all` selectors and optional aliases;
- nested `group` then child selection folders;
- rejection of `resource`, `model`, `entity`, reversed-root, and arbitrary-query selectors;
- `(expression)` parsing and `((literal))` escaping;
- literal Next.js bracket routes;
- literal/static/binary discovery;
- `_partials` exclusion;
- pack `.gitignore`, include, and exclude rules;
- `.gitignore.jinja` emission;
- engine suffix stripping and target suffix preservation;
- invalid roots/properties with suggestions;
- traversal, reserved names, cycles, shadowing, and collisions;
- imports/exports consuming planned provider/path facts;
- rejection of invented `fileName`, `filePath`, and `directory` properties.
