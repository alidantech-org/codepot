# Selections, named path recipes, descriptor patterns, and static files

## Selection is pack-owned

The pack decides which normalized records or planned artifacts each source file consumes. The project does not list internal templates, path recipes, or selection rules.

## Supported selection modes

### Once

One invocation for the project/pack context.

```yaml
selection:
  scope: project
```

### Each

One invocation per selected record.

```yaml
selection:
  each: entities
  as: entity
```

### Grouped

One invocation per deterministic group.

```yaml
selection:
  group:
    source: operations
    by: resource.name
    as: operations
```

### Aggregate

One invocation receives declared collections and may generate a monolithic file.

```yaml
selection:
  scope: aggregate
  collect:
    entities:
      from: entities
      orderBy: name
    operations:
      from: operations
      orderBy: operationId
```

### Artifact-derived

A later template may select planned artifacts or capabilities from earlier templates, for example an authored barrel, registry, package manifest, or documentation index.

## Where selection may be declared

Selection can be declared in three places:

1. a reusable named `selection`;
2. a named path recipe under `paths`;
3. an exact file descriptor.

A path-recipe selection is ideal when a whole source subtree should fan out together. A file selection is ideal when only one source file needs the alias.

## Named path recipes replace vague output-root patterns

A named path recipe composes output parts and may own fan-out:

```yaml
paths:
  module:
    selection:
      each: modules
      as: module
    parts:
      - src
      - modules
      - "[module.name.path.o]"
```

Pack content:

```text
templates/
└── {module}/
    ├── module.ts.jinja
    ├── README.md
    └── .gitkeep
```

Result:

- `module.ts.jinja` renders once per module;
- `README.md` copies once per module;
- `.gitkeep` copies once per module;
- every output begins with the parts emitted by `{module}`;
- relative source structure after `{module}` remains intact;
- no invented `module.directory` value is required.

## Nested path recipes

Recipes can compose nested selections:

```yaml
paths:
  resource:
    selection:
      each: resources
      as: resource
    parts:
      - src
      - modules
      - "[resource.name.path.o]"

  entity:
    selection:
      each: resource.entities
      as: entity
    parts:
      - entities
```

Source path:

```text
{resource}/{entity}/[entity.name.kebab.s].entity.ts.jinja
```

The `entity` recipe is valid only after a context has introduced `resource`. The planner validates alias availability before creating invocations.

## Descriptor patterns

`filePatterns` remain useful, but their primary purpose is configuring matching source descriptors rather than inventing output directories.

Examples:

```yaml
filePatterns:
  "**/*.spec.ts.jinja":
    profiles: [tests]
    localRules:
      typescript:
        comments:
          generatedHeader: test

  "_partials/**/*.jinja":
    role: partial
```

Pattern precedence is deterministic:

1. content-root defaults;
2. broad matching `filePatterns`;
3. more specific matching patterns;
4. exact `files` entry;
5. project override only when the pack explicitly exposes that field.

Conflicting values at equal specificity are errors.

## Filters and ordering

Selections use a bounded typed expression language. Supported fields and operations come from the IR/selection descriptors and are validated before invocation creation.

Templates do not query the complete source graph or perform hidden discovery. Ordering must be explicit or guaranteed by the collection contract.

## Gitignore-compatible exclusions

Packs may define inline patterns and/or `.codepotgignore`.

Supported behavior includes:

- `*` and `?` within a path segment;
- `**` across directories;
- leading `/` for content-root-relative matches;
- trailing `/` for directories;
- `!` negation;
- comments in ignore files;
- deterministic application order.

Ignored files receive no descriptor and cannot be included by templates.

## Static and binary fan-out

Static or binary content can be copied:

- once to its token-resolved relative destination;
- once for each selected record;
- once for each group;
- below a selection-bearing path recipe;
- into an owned standalone package or complete project.

Content bytes remain unchanged. Only the destination is planned.

Example:

```text
templates/{package}/.gitignore
templates/{package}/assets/logo.png
```

```yaml
paths:
  package:
    selection:
      each: packages
      as: package
    parts:
      - packages
      - "[package.name.path.o]"
```

## Profiles

Profiles choose declared source descriptors and option defaults:

```yaml
profiles:
  modular:
    enable: [entity, operation, index]
  monolithic:
    enable: [completeApi]
```

Profiles cannot activate ignored files, bypass bindings, change undeclared paths, or select a global language.

## Required tests

Tests cover:

- once, each, grouped, aggregate, and artifact-derived selections;
- deterministic filters and ordering;
- structural and selection-bearing path recipes;
- nested recipe alias scope;
- static and binary fan-out;
- descriptor-pattern precedence and conflicts;
- ignore and negation semantics;
- profile activation;
- source-path relative structure preservation;
- no hidden `fileName` or `directory` dependency;
- no source graph access from templates.
