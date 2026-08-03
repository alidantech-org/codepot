Yes. Here is the full step-by-step path from current state to **first real code generation**.

## Phase 0 — Lock boundaries

Current final architecture:

```text
src/contracts/
  spec/        normalized spec context only
  language/    language-adapted context only
  templates/   template package config + template render context only

src/spec/
  ir/          raw typed compiled IR
  kinds/       reusable stable spec enums/kinds
  repository/  converts IR → contracts/spec context

src/pipeline/
  templates/   load/validate codepotx.yaml
  selection/   resolve select syntax
  planning/    build generation plan
  pathing/     expand output paths
  language/    call language adapter
  emission/    render/copy/write files

src/languages/
  typescript/  language adapter only

src/cli/
  commands only call app.py

src/app.py
  public application API
```

Rule:

```text
contracts define shape.
spec repository builds spec context.
pipeline plans and emits.
language adapters decorate context.
templates render only.
```

---

# Phase 1 — Create `spec.kinds`

Purpose: avoid repeating stable enum/kind values.

Create:

```text
src/spec/kinds/
  __init__.py
  content.py
  primitive.py
  fields.py
  routes.py
  security.py
  urls.py
```

Move/reuse these stable enums:

```text
ContentStrategy
PrimitiveType
PrimitiveFormat
QueryOperator
FieldVisibilityLevel
FieldPersistenceMode
EntityRelationKind
HttpMethod
SecurityCredentialSource
SecurityCredentialFormat
SecurityPolicyMode
UrlEnv
UrlKind
UrlProtocol
```

Then update:

```text
spec/ir/* imports spec.kinds
contracts/spec/* imports spec.kinds where needed
```

Do **not** import `spec.ir` inside contracts.

Success:

```bash
python -m compileall src tests
pytest
cpx validate
cpx inspect
```

---

# Phase 2 — Restructure contracts into only 3 domains

Contracts folder should contain only:

```text
src/contracts/
  spec/
  language/
  templates/
```

Remove old single files if present:

```text
src/contracts/spec.py
src/contracts/language.py
src/contracts/templates.py
src/contracts/files.py
src/contracts/reports.py
src/contracts/planning.py
src/contracts/paths.py
```

Those runtime concerns move elsewhere later.

---

# Phase 3 — Write `contracts/spec`

This is the normalized repository output.

Suggested files:

```text
src/contracts/spec/
  __init__.py
  names.py
  refs.py
  metadata.py
  records.py
  content.py
  properties.py
  fields.py
  schemas.py
  security.py
  responses.py
  resources.py
  context.py
```

This should define:

```text
SpecContext
SpecMetadata
SpecCounts
SpecName
SpecRef
SpecRecord
SpecContentType
SpecPrimitive
SpecEnum
SpecComposite
SpecEntity
SpecModel
SpecDto
SpecResource
SpecOperation
SpecRoutePath
SpecRoute
SpecErrorResponse
SpecSecurity*
```

Important locked rules:

```text
All named items have .name with all casing variants.
.name.singular and .name.plural are nested casing objects.
Route paths include method_names.
Params stay in SpecContext but are not normal selectable output.
Primitives stay in SpecContext but are hidden metadata.
```

Success:

```bash
python -m compileall src tests
```

---

# Phase 4 — Migrate `SpecRepository` to return `SpecContext`

Current repository already loads real YAML and counts. Now upgrade it.

Repository must:

```text
load raw IR
normalize map records into lists
attach key/name/ref/identity
resolve/flatten useful refs
build SpecContext
return only contracts/spec models
```

Public API:

```python
SpecRepository.from_file(path)
repo.context
repo.metadata
repo.counts
repo.records(...)
```

Outside `spec/repository`, code should not import `spec.ir.*`.

Success:

```bash
cpx validate
cpx inspect
cpx inspect --schemas
cpx inspect --resources
cpx inspect --content-types
pytest
```

---

# Phase 5 — Write `contracts/templates/config`

This models user-authored `codepotx.yaml | codepotx.yml | codepotx.json`.

Folder:

```text
src/contracts/templates/config/
  __init__.py
  selection.py
  output.py
  resolve.py
  barrel.py
  language.py
  defaults.py
  settings.py
  commands.py
  template.py
  package.py
  variables.py
```

Config shape:

```yaml
version: 1
name: typescript

language:
  name: typescript
  extension: ts

defaults:
  output: generated/typescript
  global_alias: shared

templates:
  enum_files:
    kind: source
    select: enums.each
    template: src/enums/enum.ts.j2
    output:
      paths:
        - folders:
            - src
            - enums
          file: $[item.name.path].$[language.extension]
    barrel:
      enabled: true
      template: src/enums/index.ts.j2
      export: named
      output:
        paths:
          - folders:
              - src
              - enums
            file: index.$[language.extension]
```

Locked syntax:

```text
select: once
select: <subject>.<mode>

output.paths[].folders optional
output.paths[].file required

variables use $[...]
resolves use $ref:
  "#/templates/enum_files"
  "#/templates/enum_files/barrel"
```

Success:

```bash
python -m compileall src tests
```

---

# Phase 6 — Write template package loader

Create:

```text
src/pipeline/templates/
  __init__.py
  loader.py
  file_finder.py
```

Loader supports:

```text
codepotx.yaml
codepotx.yml
codepotx.json
```

Return:

```text
LoadedTemplatePackageConfig
```

It should include:

```text
template_package_path
config_file_path
format yaml/yml/json
parsed config
```

No validation beyond basic parse yet.

Success:

```bash
cpx template validate
```

can still be dummy or start showing real loaded config file.

---

# Phase 7 — Write selector parser and validation

Create:

```text
src/pipeline/templates/selection/
  parser.py
  matrix.py
  validator.py
```

Allowed selectors:

```text
content_types.all

enums.each/all/by_owner
composites.each/all/by_owner

entities.each/all/by_owner
field_sets.each/all/by_owner
models.each/all/by_owner
dtos.each/all/by_owner

resources.each/all
operations.each/all/by_resource
route_paths.each/all/by_resource
routes.each/all/by_resource

errors.each/all/by_owner

security_credentials.each/all
security_principals.each/all
security_policies.each/all

once
```

Invalid:

```text
params.each
primitives.each
resources.by_resource
resources.with_operations
operations.by_owner
routes.by_owner
enums
```

Success:

```bash
cpx template selections
cpx template validate
```

shows real validation.

---

# Phase 8 — Write output path variable registry

Create:

```text
src/pipeline/templates/variables/
  registry.py
  output.py
  template.py
```

This powers:

```bash
cpx template vars --select models.each
```

It should list two types:

```text
Output path variables
Template render variables
```

Output path variables are lightweight:

```text
project.*
language.*
template.*
global.*

item.* for .each
owner.* for .by_owner
resource.* for .by_resource
resource.* + item.* for resources.each
```

Template render variables are heavier and selection-specific:

```text
model
model.fields[]
model.fields[].lang.annotation
imports[]
dependencies.*
```

Success:

```bash
cpx template vars --select models.each
cpx template vars --select resources.each
cpx template vars --select route_paths.by_resource
```

---

# Phase 9 — Write output path validator and expander

Create:

```text
src/pipeline/templates/output/
  scanner.py
  expander.py
  validator.py
```

Validate:

```text
output.paths exists
each path has file
folders is optional list
variables exist for selection mode
no absolute paths
no escaping output root
source/barrel files match language extension
expanded paths are unique
```

No real file planning yet, just config validation and sample expansion.

Success:

```bash
cpx template validate
```

detects bad variables like:

```yaml
select: enums.all
file: $[item.name.path].ts
```

and errors clearly.

---

# Phase 10 — Write template directive scanner

Create:

```text
src/pipeline/templates/directives/
  scanner.py
  validator.py
```

Scan `.j2` files for:

```jinja
{# @codepot.select models.each #}
```

Validate:

```text
template entry select matches directive
once may omit directive
template file exists
barrel template exists
copy/template source exists
```

Success:

```bash
cpx template validate
```

checks real template files.

---

# Phase 11 — Write resolves validator

Create:

```text
src/pipeline/templates/resolve/
  refs.py
  validator.py
  compatibility.py
```

Validate:

```text
$ref starts with #/templates/
target template exists
#/templates/<id>/barrel target has barrel.enabled true
resolver subject compatible with target select
required resolvers exist based on selection dependency table
```

Dependency expectation table:

```text
composites -> enums, composites
entities   -> enums, composites, entities
models     -> enums, composites, models
dtos       -> enums, composites, models, dtos
errors     -> dtos
operations -> dtos, errors
routes     -> dtos, errors, operations, route_paths
resources  -> dtos, errors, operations, route_paths, routes, resources
```

Params and primitives are carried metadata, not emitted dependencies.

Success:

```bash
cpx template validate
```

gives clear missing resolver errors.

---

# Phase 12 — Author full TypeScript template package

Create:

```text
templates/typescript/
  codepotx.yaml
  package.json.j2
  tsconfig.json.j2
  README.md.j2
  src/
    index.ts.j2
    enums/
      enum.ts.j2
      index.ts.j2
    composites/
      composite.ts.j2
      index.ts.j2
    models/
      model.ts.j2
      index.ts.j2
    dtos/
      dto.ts.j2
      index.ts.j2
    errors/
      error.ts.j2
      index.ts.j2
    resources/
      resource.ts.j2
      route-paths.ts.j2
      routes.ts.j2
      operations.ts.j2
```

Success:

```bash
cpx template validate templates/typescript
cpx template inspect templates/typescript
```

---

# Phase 13 — Write `contracts/language`

Language context defines `.lang`.

Folder:

```text
src/contracts/language/
  __init__.py
  names.py
  types.py
  imports.py
  exports.py
  fields.py
  schemas.py
  resources.py
  routes.py
  runtime.py
  context.py
```

Language adapter adds:

```text
.lang.class_name
.lang.field_name
.lang.method_name
.lang.constant_name
.lang.annotation
.lang.optional
.lang.imports
.lang.exports
.lang.file_name
.lang.module_name
.lang.escaped
```

Global language context:

```text
language.name
language.extension
language.package_name
```

Success:

```bash
python -m compileall src tests
```

---

# Phase 14 — Build TypeScript language adapter

Create:

```text
src/languages/typescript/
  __init__.py
  adapter.py
  types.py
  names.py
  imports.py
  exports.py
  keywords.py
  runtime.py
```

Responsibilities only:

```text
primitive type mapping
field type annotation
safe names
reserved keyword escape
imports from emission index
barrel export rendering
```

Not responsible for:

```text
loading spec
selection
path planning
template rendering
writing files
```

Success:

```bash
cpx infer --language typescript
```

can still be dummy, but adapter can be unit-tested.

---

# Phase 15 — Build real selection planner

Create:

```text
src/pipeline/selection/
  resolver.py
  grouping.py
  context_keys.py
```

It takes:

```text
SpecContext
TemplatePackageConfig
--select / --template / --only filters
```

and produces selected template emissions:

```text
template_id
select
mode
selected item(s)
owner/resource bucket if grouped
```

It supports:

```text
.each
.all
.by_owner
.by_resource
once
```

Success:

```bash
cpx infer --template enum_files
cpx infer --select models.each
```

uses real config + real spec records.

---

# Phase 16 — Build output path planner

Create:

```text
src/pipeline/pathing/
  variables.py
  expander.py
  planner.py
```

It turns selected emissions into planned outputs:

```text
template_id
selected context
output path(s)
barrel output path(s)
```

Build emission index:

```text
ref -> emitted file
template_id -> emitted files
template_id/barrel -> barrel file
subject -> emitted files
output_path -> emitted file
```

Success:

```bash
cpx infer --show-paths
```

shows real output paths from `codepotx.yaml`.

---

# Phase 17 — Build dependency inference and resolver

Create:

```text
src/pipeline/dependencies/
  graph.py
  infer.py
  resolve.py
  index.py
```

It should:

```text
infer spec dependencies from SpecContext refs
use templates.<id>.resolves to map dependency subject -> template/barrel
validate missing/invalid resolvers
produce resolved dependency outputs
```

Success:

```bash
cpx infer --show-dependencies
```

shows real dependencies and resolves.

---

# Phase 18 — Build template context builder

Create:

```text
src/pipeline/templates/context/
  base.py
  factory.py
  field.py
  flatten.py
```

This creates Jinja context:

```text
base context
selection-specific context
flattened resolved refs
dependencies
imports
.lang decorations
```

Success:

```bash
cpx infer --show-context --template model_files
```

shows a real context preview.

---

# Phase 19 — Build import/export planning

Create:

```text
src/pipeline/imports/
  planner.py
```

or keep inside language adapter initially.

It uses:

```text
source output path
dependency output path or barrel
exported symbol
language adapter
```

to produce:

```text
imports[]
exports[]
```

Success:

```bash
cpx infer --show-imports
```

shows real imports.

---

# Phase 20 — Build renderer

Create:

```text
src/pipeline/emission/
  renderer.py
  static_copy.py
```

Support:

```text
Jinja templates
static copy
barrel rendering
once templates
selection templates
```

Do not write files yet.

Success:

```bash
cpx emit --dry-run
```

shows what would render/copy.

---

# Phase 21 — Build changed-aware writer

Create:

```text
src/pipeline/emission/
  writer.py
```

Behavior:

```text
create missing files
update changed files
unchanged if same
copy static if changed
never write outside output root
support --force
support --skip-static
```

Success:

```bash
cpx emit
```

actually writes generated package.

---

# Phase 22 — Add optional formatting/hooks

From `codepotx.yaml`:

```yaml
commands:
  format: pnpm prettier --write .
  typecheck: pnpm tsc --noEmit
```

CLI flags:

```text
--format
--run-hooks
```

Safe behavior first:

```text
print command
do not execute unless flag enabled
execute in output folder
```

Success:

```bash
cpx emit --format
cpx emit --run-hooks
```

---

# Phase 23 — Real generated TypeScript package test

Final smoke:

```bash
cpx template validate templates/typescript
cpx validate codepot.v1.yaml
cpx inspect codepot.v1.yaml
cpx infer codepot.v1.yaml --language typescript --template-package templates/typescript
cpx emit codepot.v1.yaml --language typescript --template-package templates/typescript --out .output/typescript
cd .output/typescript
pnpm install
pnpm tsc --noEmit
```

---

## Short version of the next immediate tasks

Do this next:

```text
1. spec.kinds
2. contracts/spec folder
3. repository returns SpecContext
4. contracts/templates/config folder
5. template config loader
6. selector parser/validator
7. output variable registry
8. template validate/inspect/vars becomes real
9. author full TypeScript templates
10. real infer path planning
```

Once step 10 works, we are ready to start actual render/write code generation.
