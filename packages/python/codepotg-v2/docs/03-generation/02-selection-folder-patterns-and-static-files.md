# Selections, folder patterns, and static files

## Selection is pack-owned

The pack decides which normalized records or planned artifacts each file consumes. The project does not list internal templates or selection rules.

## Supported invocation modes

### Once

One invocation for the pack/project context.

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

A later template may select planned artifacts or capabilities from earlier templates, for example an authored barrel or registry.

## Filters and ordering

Selections use a bounded typed expression language. Supported operations are declared by the IR/selection contract and validated before execution.

Templates do not query the complete source graph or perform hidden discovery.

Ordering must be explicit or defined by the collection contract so output remains deterministic.

## Folder patterns

Folder patterns apply shared selection and output defaults to matching discovered files.

Example pack content:

```text
templates/
└── {module}/
    ├── module.ts.jinja
    ├── README.md
    └── .gitkeep
```

Manifest:

```yaml
filePatterns:
  "{module}/**":
    selection:
      each: modules
      as: module
    output:
      root: src/modules/{module.directory}
```

Result:

- template content renders once per module;
- static README copies once per module;
- static `.gitkeep` copies once per module;
- relative structure below the pattern is preserved unless an exact file override changes it.

This keeps the useful fan-out behavior of tokenized folders without retaining a separate old folder execution subsystem.

## Pattern precedence

1. content-root defaults;
2. broad matching `filePatterns`;
3. more specific matching patterns;
4. exact `files` entry;
5. project override only when the pack exposes that field.

Conflicting values at equal specificity are errors rather than ordering accidents.

## Gitignore-compatible exclusions

Packs may define inline patterns and/or `.codepotgignore`.

Supported behavior should match familiar Gitignore rules:

- `*` and `?` within a path segment;
- `**` across directories;
- leading `/` for content-root-relative matches;
- trailing `/` for directories;
- `!` negation;
- comments in ignore files;
- deterministic application order.

Ignored files do not receive descriptors and cannot be included by templates.

## Static file fan-out

Static content can be copied:

- once to its relative destination;
- once for each selected record;
- once for each group;
- under a folder-pattern output root;
- into an owned standalone package or full project.

Static bytes remain unchanged. Path variables are resolved by the planner.

## Profiles

Profiles choose declared files and defaults:

```yaml
profiles:
  modular:
    enable: [entity, operation, index]
  monolithic:
    enable: [completeApi]
```

Profiles cannot activate ignored files, bypass bindings, or select a global language.

## Tests

Required tests cover:

- once, each, grouped, aggregate, and artifact-derived selection;
- deterministic filters and ordering;
- folder token binding;
- static fan-out;
- pattern precedence and conflicts;
- ignore and negation semantics;
- profile activation;
- no source graph access from templates.
