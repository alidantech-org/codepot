# Root-first fixed selections, selection folders, dependencies, barrels, and static files

## Selection is pack-owned but kernel-defined

The project chooses a pack and its semantic input. The pack chooses among documented fixed selectors to drive each registered emission selection.

The project never lists internal template files or selection rules. The pack cannot invent selector grammar, semantic roots, facets, graph queries, traversal, or filters.

## Root-first selector registry

Selectors start with the outer semantic scope and traverse inward.

Preferred initial selectors include:

```text
groups.each / groups.all
groups.schemas.each / groups.schemas.all
groups.schemas.objects.each / groups.schemas.objects.all
groups.schemas.enums.each / groups.schemas.enums.all
groups.schemas.dtos.each / groups.schemas.dtos.all
groups.operations.each / groups.operations.all
groups.operations.inputs.each / groups.operations.inputs.all
groups.operations.outputs.each / groups.operations.outputs.all
groups.operations.failures.each / groups.operations.failures.all
groups.views.each / groups.views.all
groups.storage.mappings.each / groups.storage.mappings.all
groups.workflows.each / groups.workflows.all
groups.policies.each / groups.policies.all
groups.events.each / groups.events.all
```

Inside an active group context, parent-scoped selectors use the singular outer context first:

```text
group.schemas.each
group.operations.each
group.views.each
group.storage.mappings.each
group.workflows.each
group.policies.each
group.events.each
```

`.each` creates one context per selected item. `.all` creates one context containing the selected collection. Default context names are inferred from the selector. Optional aliases are inline:

```yaml
select: groups.operations.each(apiOperation)
```

Aliases may not shadow active contexts.

Global selectors such as `operations.each` or `schemas.all` may be supported for genuine project-wide indexes and reports, but they are discouraged for ordinary generation. A pack should select `groups.operations` rather than select all operations and reconstruct group ownership in the template.

The registry does not expose:

```text
resources.each
entities.each
schemas.models.each
resource.operations.each
http.groups.each
storage.mappings.each
events.operations.each
```

Nor does it accept arbitrary structures such as:

```yaml
select:
  kind: operation
  where: {}
  traverse: {}
```

When a repeated real-world need requires a filtered view, CodepotG adds a named fixed selector through a kernel/selection behavior version.

## One selection registry

```yaml
selections:
  persistenceTypes:
    paths: [src, persistence]
    select: groups.storage.mappings.each
    symbols:
      - (mapping.schema.name.pascal.s)Entity

  repositories:
    paths: [src, repositories]
    select: groups.storage.mappings.each
    imports:
      persistenceType: persistenceTypes
    bindings: [baseRepository]
    symbols:
      - (mapping.schema.name.pascal.s)Repository
```

The selection key is:

- the manifest identity of the emission group;
- the folder key used by `templates/{selectionKey}/`;
- the dependency key referenced by `imports` or `exports`.

No secondary artifact namespace or hidden selection alias is required.

## Selection folders

```text
templates/{repositories}/(mapping.schema.name.kebab.s).repository.ts.jinja
```

`{repositories}` is replaced by:

```yaml
paths: [src, repositories]
```

The file repeats according to:

```yaml
select: groups.storage.mappings.each
```

Every included descendant under the selection folder inherits the same immutable selection context and output prefix.

## Nested group-scoped selection folders

```yaml
selections:
  groupModules:
    paths: [src, modules, (group.name.path.o)]
    select: groups.each

  operations:
    paths: [operations]
    select: group.operations.each
```

```text
templates/{groupModules}/{operations}/(operation.name.kebab.s).operation.ts.jinja
```

Selection folders are resolved left to right. `operations` may use the active `group` context established by `groupModules`.

The context order remains:

```text
group
→ group.operations
→ operation
→ operation.facets.http
```

No reversed `http.group` or `operations.group` context is introduced.

## Pack-root emission

`{root}` is built in:

```text
templates/{root}/package.json.jinja -> package.json
```

It allows physical grouping without an output folder.

## Imports are explicit semantic dependencies

```yaml
repositories:
  paths: [src, repositories]
  select: groups.storage.mappings.each
  imports:
    persistenceType: persistenceTypes
```

The mapping is `localName: selectionKey`.

The dependency resolver:

- accepts only declared selection providers;
- matches consumer/provider artifacts through selected semantic identity and active scope;
- matches required names to explicitly declared symbols;
- supplies only the required provider modules and symbols;
- respects `.each`, `.all`, project-wide, and active-parent scopes;
- rejects missing, ambiguous, duplicate, conflicting, or cyclic providers;
- resolves provider destination and target-aware module/path facts before rendering;
- exposes immutable dependency descriptors under the declared local name.

The template writes all syntax. For example:

```jinja
{% for module in imports.persistenceType.modules %}
import { {{ module.symbols | join(", ") }} } from "{{ module.specifier }}";
{% endfor %}
```

Another target may author different syntax from the same facts. CodepotG and language adapters do not inject import statements.

A direct `.each` provider may produce several module descriptors. A group-rooted `.all` or barrel provider may produce one aggregate descriptor. The provider selection and semantic match determine the shape.

## Barrels and exports

A barrel is a normal authored template whose selection declares ordered exports:

```yaml
repositoriesIndex:
  paths: [src, repositories]
  exports: [repositories]
```

```text
templates/{repositoriesIndex}/index.ts.jinja
```

The template receives `exports.repositories`, including emitted paths, module/path facts, semantic identities, and declared symbols. It controls wildcard, explicit, aliased, type-only, comments, formatting, and textual order.

A barrel may export another barrel:

```yaml
rootIndex:
  paths: [src]
  exports: [persistenceIndex, repositoriesIndex]
```

Missing keys and export cycles are rejected before rendering.

## Aggregate templates

A template selecting a complete semantic collection uses `.all`:

```yaml
groupOperationRegistry:
  paths: [src, generated]
  select: groups.operations.all
  symbols: [OperationRegistry]
```

A template aggregating emitted files uses `exports` instead. Semantic collections and generated artifacts are not conflated.

## Literal, static, and binary content

Content outside a selection folder follows its literal relative path:

```text
templates/README.md.jinja -> README.md
templates/assets/logo.png -> assets/logo.png
```

Inside a selection folder, literal/static descendants repeat with that selection:

```text
templates/{groupModules}/README.md
templates/{groupModules}/assets/icon.png
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

- kernel semantic collections provide deterministic order;
- outer group scope is established before inner collections;
- `exports` preserves declared selection-key order;
- individual emissions use deterministic semantic/path/scope order;
- templates control textual ordering using supplied descriptors.

## Required tests

- root-first fixed `.each` and `.all` selectors;
- active-parent selectors such as `group.operations.each`;
- discouraged global selector diagnostics/documentation;
- rejection of `resource`, `entity`, `model`, reversed-root, and arbitrary-query selectors;
- optional aliases and shadowing rejection;
- selection-folder fan-out and nested group scope;
- `{root}`;
- semantic provider matching and least-required symbols;
- template-authored import/export syntax;
- direct versus barrel dependencies;
- barrels exporting barrels;
- aggregate semantic templates versus emitted-file barrels;
- static/binary fan-out;
- ignore/include/exclude behavior;
- deterministic ordering;
- unknown keys, missing imports, symbol conflicts, cycles, traversal, and collisions.
