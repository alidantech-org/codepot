Yes. Let’s recap and lock the **template authoring layer** before writing code.

## 1. What we are building now

We are not building final generation yet. We are building the **user-facing template package system**.

This layer lets a template author write:

```text
templates/typescript/codepotx.yaml
templates/typescript/**/*.j2
templates/typescript/static files
```

Then Codepotx can:

```text
load template package
validate selections
validate template declarations
validate output paths
validate resolves
list available variables
infer planned files
later render/write
```

## 2. Final template package config

One config file only:

```text
codepotx.yaml
codepotx.yml
codepotx.json
```

No `paths.yaml`.

Config shape:

```yaml
version: 1

name: typescript
label: TypeScript package

language:
  name: typescript
  extension: ts
  package_manager: pnpm

defaults:
  output: generated/typescript
  global_alias: shared

settings:
  require_template_select: true
  validate_unique_outputs: true
  validate_resolves: true

templates:
  enum_files:
    kind: source
    select: enums.each
    template: enum/enum.ts.j2
    output:
      paths:
        - folders:
            - src
            - enums
          file: "{item.name.path}.ts"

  model_files:
    kind: source
    select: models.each
    template: model/model.ts.j2
    output:
      paths:
        - folders:
            - src
            - models
          file: "{item.name.path}.ts"
    resolves:
      enums:
        $ref: "#/templates/enum_files/barrel"
      composites:
        $ref: "#/templates/composite_files"
      models:
        $ref: "#/templates/model_files"
```

## 3. Selection syntax

Locked:

```text
<subject>.<mode>
```

or:

```text
once
```

Modes:

```text
.each        one file per item
.all         one file for all selected items
.by_owner    one file per owner bucket
.by_resource one file per resource
once         one global file
```

Important locked rule:

```text
resources.each = one file per resource with full resource context
```

No:

```text
resources.with_operations
resources.by_resource
```

## 4. Selectable subjects

Allowed:

```text
content_types

enums
composites

entities
field_sets
models
dtos

resources
operations
route_paths
routes

errors

security_credentials
security_principals
security_policies
```

Hidden / not normally selectable:

```text
primitives
params
```

Reason:

```text
primitives = language type metadata
params = carried route/operation/path context
```

## 5. Route path rule

`route_paths` is a real selectable subject.

Allowed:

```text
route_paths.each
route_paths.all
route_paths.by_resource
```

Route path context includes:

```text
route_path.path
route_path.parameters
route_path.params
route_path.method_names
route_path.methods
resource
```

Example:

```text
route_path.method_names = ("get", "post")
```

## 6. Dependency / resolves design

No `depends_on`.

Only:

```yaml
resolves:
  enums:
    $ref: "#/templates/enum_files"
  models:
    $ref: "#/templates/model_files"
```

Or resolve through a barrel:

```yaml
resolves:
  enums:
    $ref: "#/templates/enum_files/barrel"
```

Meaning:

```text
When this template needs enum imports, resolve enum dependencies through enum_files or enum_files.barrel.
```

The runtime already knows possible dependency subjects from spec graph.

Example error:

```text
Template: model_files
Select: models.each
Missing resolver: enums

Add:
resolves:
  enums:
    $ref: "#/templates/enum_files"
```

## 7. Barrel support

A template may define:

```yaml
barrel:
  enabled: true
  template: enum/index.ts.j2
  export: named
  output:
    paths:
      - folders:
          - src
          - enums
        file: index.ts
```

Then another template may resolve to:

```yaml
$ref: "#/templates/enum_files/barrel"
```

Barrel is not a normal selector. It receives emission/export context from its parent template.

Export strategies:

```text
named default
star
```

Language adapter prepares exports/imports.

## 8. Output path design

Only one shape:

```yaml
output:
  paths:
    - folders:
        - src
        - "{resource.folders}"
        - "{resource.name.path}"
      file: index.ts
```

Rules:

```text
folders optional
file required
file may contain /
final path = folders + file
no absolute paths
no escaping output root
source files must match language extension
expanded paths must be unique
```

## 9. Lightweight output path variables

Output path variables are smaller than template context.

Always available:

```text
project.key
project.title
project.version
project.spec_version
project.codepot_version

language.name
language.extension
language.package_name

template.id
template.kind
template.select
template.subject
template.mode

global.alias
```

For `.each`:

```text
item.key
item.ref
item.identity.raw
item.identity.owner_identity
item.identity.owner_key
item.identity.local_key
item.name.*
```

For `.by_owner`:

```text
owner.key
owner.ref
owner.folders
owner.name.*
```

For `.by_resource`:

```text
resource.key
resource.ref
resource.folders
resource.base_path
resource.name.*
```

For `resources.each`, both are available:

```text
item.*
resource.*
```

For `once`:

```text
project.*
language.*
template.*
global.*
```

No `item`, `owner`, or `resource`.

## 10. Naming shape

Every named thing gets:

```text
name.raw
name.clean
name.pascal
name.camel
name.snake
name.kebab
name.screaming_snake
name.constant
name.path
```

Plural and singular are nested casing objects:

```text
name.singular.path
name.singular.pascal
name.singular.camel
name.singular.snake

name.plural.path
name.plural.pascal
name.plural.camel
name.plural.snake
```

No direct:

```text
name.singular
name.plural
```

## 11. Template render context model

Every template gets base context:

```text
global
project
spec
language
template
path
```

Then selection-specific context.

Examples:

```text
enums.each
  enum
  item
  owner
  dependencies
  imports

models.each
  model
  item
  owner
  fields
  dependencies
  imports

dtos.by_owner
  owner
  dtos[]
  items[]
  dependencies
  imports

resources.each
  resource
  item
  operations[]
  route_paths[]
  routes[]
  defaults
  dependencies
  imports

operations.by_resource
  resource
  operations[]
  items[]
  dependencies
  imports

route_paths.each
  route_path
  item
  resource
  parameters
  params
  method_names[]
  methods[]

once
  global/project/spec/language/template/path only by default
```

## 12. Language adapter role

Language adapter stays simple. It decorates context with `.lang`.

It handles:

```text
primitive type mapping
type annotations
imports
exports
class names
method names
field names
reserved keyword escaping
file/module names
```

Example:

```text
field.required
field.nullable
field.array
field.type
field.format
field.validation

field.lang.field_name
field.lang.annotation
field.lang.optional
field.lang.imports
```

Templates should generally render `.lang`, but may inspect flattened spec data for customization.

## 13. Ref flattening rule

If a field refs a primitive, the resolved primitive data is copied onto the field context.

Example:

```text
field.ref = #/properties/primitives/email
field.source.kind = primitive
field.type = string
field.format = email
field.validation = ...
```

This keeps templates simple. Template authors should not resolve refs manually.

## 14. Template declarations

Selectable templates must declare:

```jinja
{# @codepot.select models.each #}
```

The runtime validates:

```text
template config select == template declared select
```

For `once`, declaration may be optional.

## 15. How we list variables

We need a command or inspect mode later:

```bash
cpx templates inspect templates/typescript
cpx templates variables templates/typescript --select models.each
```

Or integrated into existing CLI:

```bash
cpx inspect --template-context models.each
```

I suggest a future command:

```text
cpx template vars --select models.each --language typescript
```

It should show:

```text
Output path variables
  item.name.path
  owner.name.path
  project.key
  language.extension

Template variables
  model.name.*
  model.fields[].*
  model.fields[].lang.*
  imports[]
  dependencies.*
```

This is how template authors learn what is available.

## Implementation plan, no code yet

### Phase 1: config contracts

Create/adjust contracts for:

```text
TemplatePackageConfig
TemplateEntryConfig
TemplateBarrelConfig
TemplateOutputConfig
TemplateOutputPathConfig
TemplateResolveRef
TemplateSettings
TemplateLanguageConfig
```

### Phase 2: config loader

Load:

```text
codepotx.yaml
codepotx.yml
codepotx.json
```

Validate:

```text
templates map exists
template IDs valid
select syntax valid
output paths valid
resolves refs valid
barrel refs valid
template/copy source exists
```

### Phase 3: selector model

Parse:

```text
models.each
operations.by_resource
once
```

into:

```text
subject
mode
```

Validate subject/mode support matrix.

### Phase 4: output variable registry

Build a registry of allowed output path variables per select mode.

This registry powers both:

```text
validation
variable listing command
```

### Phase 5: template directive scanner

Read `.j2` files and find:

```text
@codepot.select <selector>
```

Validate against config.

### Phase 6: dependency resolver validation

Validate:

```text
resolves refs point to existing templates/barrels
resolver target selects compatible subject
required dependency subjects are resolved
```

### Phase 7: variable listing

Add a way to list:

```text
output path variables
template render variables
```

per selection.

## Next decision to make

Before code, we should lock this:

Should variable listing be a new command:

```bash
cpx template vars --select models.each
```

or added under existing inspect:

```bash
cpx inspect --template-vars models.each
```

My advice: add it later as a new command group:

```text
cpx template validate
cpx template vars
cpx template inspect
```

because this is about template packages, not the spec itself.
