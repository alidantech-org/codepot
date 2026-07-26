# Path expressions, named path recipes, and name tokens

## Core rule

The relative source path of a pack file is its default output-path program.

CodepotG does not expect semantic records such as `entity`, `model`, `operation`, or `resource` to expose invented properties such as `fileName`, `filePath`, or `directory`. A pack author composes the output location directly from:

- literal path segments already present in the pack source tree;
- named path recipes referenced with `{recipe}`;
- bounded typed values referenced with `[expression]`;
- explicit casing and original/singular/plural name projections;
- the target and template-engine suffixes already present on the source filename.

For example:

```text
templates/{repositories}/[entity.name.kebab.s].repository.ts.jinja
```

may resolve to:

```text
src/repositories/order.repository.ts
```

The final `.jinja` engine suffix is removed. The `.ts` target suffix remains. No `entity.fileName` property is involved.

## Path syntax

CodepotG v2 supports four source-path token forms:

```text
{recipe}       named path recipe
[expression]   bounded typed path expression
[[value]]      literal bracketed value: [value]
{{value}}      literal braced value: {value}
```

Examples:

```text
{models}/[model.name.kebab.s].model.ts.jinja
{resource}/[resource.name.path.o]/index.ts.jinja
app/[[...slug]]/page.tsx.jinja
routes/{{id}}/handler.ts.jinja
```

The escaping forms are required for targets such as Next.js route folders where brackets or braces are literal output characters.

## Named path recipes

`CodepotgPack.yaml` may declare reusable named path recipes under `paths`:

```yaml
paths:
  repositories:
    parts:
      - src
      - repositories

  resource:
    selection:
      each: resources
      as: resource
    parts:
      - src
      - modules
      - "[resource.path]"
      - "[resource.name.path.o]"

  entity:
    selection:
      each: resource.entities
      as: entity
    parts:
      - entities
```

A recipe has two independent responsibilities:

1. it may contribute zero or more destination path parts;
2. it may introduce a selection alias and fan out every matching descendant file.

A structural recipe may have only `parts`. A fan-out recipe may have `selection` and `parts`. A selection-only recipe may emit no parts.

## Left-to-right composition and alias scope

Path tokens are evaluated from left to right.

```text
{resource}/{entity}/[entity.name.kebab.s].entity.ts.jinja
```

Resolution proceeds as follows:

1. `{resource}` selects each resource as `resource` and emits its configured parts;
2. `{entity}` may reference the active `resource`, selects `resource.entities` as `entity`, and emits `entities`;
3. `[entity.name.kebab.s]` resolves from the active entity alias;
4. `.entity.ts` is preserved as literal filename text;
5. `.jinja` is stripped as the engine suffix.

Aliases introduced by earlier recipe tokens are available to later recipes and expressions. An alias may not be silently shadowed. Recursive recipe references and selection cycles are rejected during planning.

## File-level selections

A file descriptor may still declare a named or inline selection when the source path does not introduce it:

```yaml
paths:
  repositories:
    parts: [src, repositories]

selections:
  entities:
    from: entities
    as: entity

files:
  "{repositories}/[entity.name.kebab.s].repository.ts.jinja":
    id: repository
    role: template
    selection:
      use: entities
```

The file selection is established before its dynamic path expressions are resolved.

Recipe-owned selection is preferred when an entire folder tree, including static files, should fan out together. File-owned selection is preferred when only one file needs the selected context.

## Name token contract

Every neutral semantic item with a meaningful authored name exposes a typed `name` value. The stable case projections are:

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

Examples:

```text
[entity.name.pascal.s]
[entity.name.kebab.p]
[resource.name.path.o]
[operation.name.camel.o]
[enum.name.screaming.s]
```

Long names are also supported:

```text
[entity.name.pascal.singular]
[resource.name.path.original]
[model.name.snake.plural]
```

`original` preserves the source lexical number. `singular` and `plural` are produced by the configured, behavior-versioned inflection service. Irregular and uncountable names must be deterministic and testable. The naming/inflection behavior version participates in lock and cache identities.

## Path values and scalar values

A path expression resolves to one of a small set of typed values:

- path-safe scalar;
- semantic name projection;
- `PathSegments`;
- optional path-safe value;
- registered namespaced path value.

A `PathSegments` value such as `resource.path` may expand into several destination segments when the expression occupies the whole source segment:

```text
{root}/[resource.path]/[resource.name.path.o]/index.ts.jinja
```

A multi-segment value may not be embedded inside a filename. This is invalid:

```text
prefix-[resource.path].ts.jinja
```

Sequences are never joined through hidden stringification. A pack must use a typed, declared join or projection when joining is required.

## Stable expression roots

The initial registry should support typed descriptors for:

- current selection aliases such as `resource`, `entity`, `operation`, or `model`;
- `project` identity and declared project variables;
- `pack` identity and version;
- named `source` metadata;
- selected project `unit` metadata;
- `option` values declared by the pack;
- path-safe `binding` values;
- deterministic `group` keys;
- already planned `artifact` paths where the dependency graph permits them;
- target metadata such as the resolved target ID and suffix.

Plugins may register additional namespaced path values only through typed descriptors. A template pack cannot register executable path code.

## Expression safety

`[expression]` is not Jinja, Python, JavaScript, or arbitrary attribute access.

The path-expression compiler validates every root and property against registered typed descriptors. It must reject:

- method calls;
- arbitrary indexing;
- unregistered properties;
- parser/source implementation objects;
- environment-variable access not declared as a binding;
- filesystem reads;
- non-deterministic values;
- values that cannot become safe path segments.

Diagnostics must identify the source path, token span, unknown property, and available alternatives.

## Source path to destination algorithm

For each discovered source file:

1. determine its content-root-relative source path;
2. establish any exact file selection;
3. parse static, recipe, dynamic, and escaped tokens;
4. expand named recipes left to right, including nested selection fan-out;
5. resolve typed expressions;
6. preserve literal prefixes, suffixes, and target extensions;
7. remove only the recognized template-engine suffix for emitted templates;
8. preserve the complete relative path for static/binary files after token expansion;
9. normalize and validate every path segment;
10. prepend the project pack-instance output root;
11. reject traversal, absolute paths, reserved segments, case collisions, and duplicate destinations.

## Explicit output overrides

Most files should not need an `output` field. Their source path is already the output recipe.

An explicit override is allowed only when the pack source layout cannot reasonably represent the destination or when one template declares multiple named outputs. It uses the same typed path grammar:

```yaml
files:
  "authoring/combined.ts.jinja":
    id: combined
    role: template
    selection:
      scope: aggregate
    output:
      parts:
        - gen
        - "[project.name.kebab.o]-sdk.ts"
```

An override does not unlock Jinja expressions or arbitrary path creation. Named outputs must all be declared before rendering.

## Static files and tokenized folders

Static and binary files use the same source-path program:

```text
templates/{package}/.gitignore
templates/{package}/assets/logo.png
templates/{resource}/README.md
```

If `{package}` or `{resource}` owns a selection, the unchanged bytes are copied once per selected context into the resolved path. This preserves the strongest part of the former folder design without a separate static-emission subsystem.

## Authored barrels

A barrel remains an ordinary template file:

```text
templates/{modelsRoot}/index.ts.jinja
```

Its path is composed by the same rules as every other template. The manifest marks it `role: barrel` and declares which artifact providers it exports. The template owns comments and output text; the planner only supplies the typed export context.

## Adapter responsibilities

Core owns path syntax, name projections, inflection, token parsing, and safe path composition.

A target-language adapter:

- declares target extensions;
- validates final filenames for target-specific restrictions;
- may expose typed namespaced target path values;
- does not invent `fileName` properties on IR records;
- does not select output folders;
- does not parse template source paths itself.

An ecosystem adapter may expose typed project-unit or package path values. A template-engine adapter has no authority over output path planning.

## Required tests

The path subsystem must test:

- every case and original/singular/plural name projection;
- irregular and uncountable names;
- nested named recipes and alias scope;
- structural, selection-only, and selection-plus-parts recipes;
- file-owned selections;
- static and binary fan-out;
- embedded scalar tokens and multi-segment path values;
- literal bracket and brace escaping;
- engine suffix stripping and target suffix preservation;
- Next.js-style literal route names;
- invalid roots/properties with suggestions;
- cycles, alias shadowing, traversal, reserved names, and collisions;
- deterministic behavior and cache-key changes when naming behavior changes;
- explicit output overrides and multiple declared outputs;
- rejection of invented `fileName` and `directory` properties.
