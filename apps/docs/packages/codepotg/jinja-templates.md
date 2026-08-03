---
title: Writing Jinja templates
description: Render normalized CodepotG context safely with variables, filters, includes, macros, whitespace control, and imports.
product: codepotg
package: codepotg
order: 8
---

# Writing Jinja templates

CodepotG uses Jinja templates to turn a planned render context into target files.

## Basic model template

```jinja
{# models/model.ts.j2 #}
export interface {{ model.name.pascal }} {
{% for field in model.fields %}
  {{ field.name.camel }}{{ "?" if not field.required else "" }}: {{ field.lang.type }};
{% endfor %}
}
```

The output path is controlled by `paths.yaml`, not by the template.

## Context boundaries

A graph emission receives:

- global project and language information;
- its declared selection alias;
- explicit provider outputs;
- file/emission metadata;
- lazy resolvers allowed by the pack contract.

Do not assume every template receives every schema, operation, entity, or raw OpenAPI object. Bounded contexts are deliberate.

## Normalized values first

Use this lookup order:

1. normalized named property;
2. normalized derived view;
3. `extensions`;
4. object `raw`;
5. root `api.raw`.

For example, prefer:

```jinja
{{ field.constraints.max_length }}
```

over direct raw access to `maxLength`.

## Filters

CodepotG and language adapters provide filters for common needs such as:

- casing and identifiers;
- plural and singular forms;
- target-language types;
- literals;
- imports;
- comments and documentation;
- file-safe names.

Use the installed pack's documented filters. Do not recreate naming behavior in every template with custom string slicing.

## Includes

Use includes for reusable fragments that render with the current context:

```jinja
{% include "partials/header.ts.j2" %}
```

## Macros

Use macros for parameterized rendering:

```jinja
{% macro render_field(field) -%}
  {{ field.name.camel }}: {{ field.lang.type }};
{%- endmacro %}
```

Keep macros deterministic and side-effect free.

## Template inheritance

Jinja inheritance is useful for closely related files with a stable shared shell. Avoid deep inheritance trees that hide where generated code comes from.

## Whitespace control

Use `-%}` and `{%-` deliberately. Generated source should be stable across runs and format cleanly before optional post-generation formatters.

Do not rely on a formatter to repair structurally incorrect output.

## Imports and dependencies

Prefer planned import facts supplied by the emission context:

```jinja
{% for import in file.imports %}
{{ import.rendered }}
{% endfor %}
```

The exact shape depends on the language adapter and pack contract. Avoid rediscovering dependencies by scanning field refs in Jinja when the planner already resolved them.

## Conditional output

Use Jinja conditions for target syntax:

```jinja
{% if model.docs.description %}
/** {{ model.docs.description }} */
{% endif %}
```

Use `paths.yaml` conditions or selections to decide whether an entire file should exist.

## Raw files

Files that must be copied exactly should use raw/static-file support rather than escaping every Jinja delimiter.

## Debugging

Use the debug language/pack or a temporary diagnostic template to inspect bounded values. Keep debug output outside managed production paths.

```bash
codepotg generate debug-context --dry-run --verbose
```

## Safety

Templates are project code. Review filters, includes, path expressions, and raw access. Keep output paths controlled by the pack planner and lifecycle policy.