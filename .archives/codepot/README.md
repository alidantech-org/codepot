Here is the **final recommended file structure**.

```text
codepot/
  spec.v1.yaml
  pyproject.toml
  README.md

  templates/
    python/
      enum.py.j2
      model.py.j2
      dto.py.j2
      resource.py.j2
      __init__.py.j2
    paths.template.yaml

  tests/
    __init__.py
    conftest.py
    spec/
    app/
    languages/

  src/
    __init__.py

    app.py

    cli/
      __init__.py
      main.py
      bootstrap.py
      commands/
        __init__.py
        inspect.py
        validate.py
        infer.py
        emit.py
      constants/
        __init__.py
        constants.py
        defaults.py
      presentation/
        __init__.py
        core/
          __init__.py
          console.py
          diagnostics.py
          interactive.py
          tables.py
        inspect/
        validate/
        infer/
        emit/

    contracts/
      __init__.py
      repository.py
      planning.py
      language.py
      paths.py
      templates.py
      files.py

    spec/
      __init__.py
      loader/
        __init__.py
        yaml_loader.py
      repository/
        __init__.py
        document.py
        records.py
        record_sets.py
        query.py
        refs.py
        graph.py
      ir/
        __init__.py
        shared/
          __init__.py
          ref.py
          base.py
          info.py
          url.py
          content.py
          document.py
        properties/
          __init__.py
          definition.py
          primitive/
            __init__.py
            definition.py
          enum/
            __init__.py
            definition.py
          composite/
            __init__.py
            definition.py
        schema/
          __init__.py
          definition.py
          entity/
            __init__.py
            definition.py
            field/
              __init__.py
              definition.py
          field_set/
            __init__.py
            definition.py
          model/
            __init__.py
            definition.py
          dto/
            __init__.py
            definition.py
          params/
            __init__.py
            definition.py
        resource/
          __init__.py
          definition.py
          operation/
            __init__.py
            definition.py
          route/
            __init__.py
            definition.py
        response/
          __init__.py
          definition.py
          errors/
            __init__.py
            definition.py
        security/
          __init__.py
          definition.py

    app/
      __init__.py
      pipeline.py
      selection/
        __init__.py
        kinds.py
        config.py
        resolver.py
      pathing/
        __init__.py
        identity.py
        branch.py
        variables.py
        planner.py
      planning/
        __init__.py
        records.py
        pipeline.py
      adapter/
        __init__.py
        languages.py
      emission/
        __init__.py
        file_plan.py
        renderer.py
        writer.py

    languages/
      __init__.py
      contracts.py
      registry.py
      python/
        __init__.py
        adapter.py
        names.py
        types.py
        imports.py
        keywords.py

    utils/
      __init__.py
      naming/
        __init__.py
        aliases.py
        cases.py
        number.py
        plurality.py
        provider.py
      collections/
        __init__.py
      files/
        __init__.py
      templates/
        __init__.py
      types/
        __init__.py
```

## Explanation by layer

### 1. Root files

```text
spec.v1.yaml
pyproject.toml
README.md
```

These are project-level files.

`spec.v1.yaml` is only a sample/test compiled spec.

---

### 2. `templates/`

```text
templates/
  python/
  paths.template.yaml
```

This is user-customizable output layout and rendering.

`paths.template.yaml` decides:

```yaml
select: enums
branch: by_owner
template: python/enum.py.j2
output: ...
```

Templates should not calculate names, paths, imports, or types. They only render prepared context.

---

### 3. `src/app.py`

This is the public Python API.

CLI calls this. Future integrations call this.

Example responsibilities:

```text
inspect_spec()
validate_spec()
infer_spec()
emit_spec()
```

It should delegate to `src/pipeline/pipeline.py`.

---

### 4. `src/cli/`

CLI is just an interface.

It should not know repository internals, language internals, or template internals.

Good dependency:

```text
cli → app.py
```

Bad dependency:

```text
cli → spec.ir.*
cli → languages.python.*
cli → templates
```

---

### 5. `src/contracts/`

This holds shared context contracts.

Examples:

```text
RepositoryRecord
SelectedRecord
PlannedItem
LanguageItem
PathVariables
TemplateContext
PlannedFile
RenderedFile
WriteReport
```

Use this when a model is shared between layers.

Do not put runtime behavior here. Keep it as typed contracts.

---

### 6. `src/spec/`

This is the compiled spec database layer.

It replaces old `codepot/ir` naming. Since the package is already Codepot, `spec` is cleaner.

#### `spec/ir/`

Typed Python models matching the TS IR definitions.

These are the schema/database tables.

#### `spec/loader/`

Loads YAML into typed IR models.

#### `spec/repository/`

This is the only public API from `spec`.

Outside layers should use:

```python
from spec.repository import SpecRepository
```

They should not import raw IR models directly.

Repository responsibilities:

```text
normalize maps into records
resolve refs
query records
build dependency graph
expose typed record sets
```

Add `query.py` here for typed filtering helpers.

---

### 7. `src/pipeline/`

This is the generation pipeline layer.

It answers:

```text
What do we generate?
How do we group it?
What file plan do we produce?
When do we call language adapters?
When do we render/write?
```

#### `app/pipeline.py`

The only orchestrator.

It can import:

```text
spec.repository
app.selection
app.pathing
app.planning
app.adapter
app.emission
languages
```

Other files should not randomly cross layers.

#### `app/selection/`

Handles:

```yaml
select: enums
select: models
select: resources
```

No arbitrary `eval` filters.

#### `app/pathing/`

Handles dot-key parsing and path variables.

Important rule:

```text
entity.user.nickname
```

does not mean folders directly.

It means:

```text
owner identity = entity
owner key      = user
local key      = nickname
```

Path planner decides folders later.

#### `app/planning/`

Language-neutral generation plan.

No Python/Dart/TS decisions here.

#### `app/adapter/`

Bridge between app pipeline and `languages/`.

This prevents pipeline from knowing language implementation details.

#### `app/emission/`

File planning, rendering, and writing.

It owns:

```text
PlannedFile
RenderedFile
WriteReport
template rendering
changed-aware writing
dry run
```

---

### 8. `src/languages/`

Languages are first-class but simple.

They do not own the full pipeline.

They only handle:

```text
type mapping
reserved keyword conflicts
language-safe names
imports
file extensions
small language conventions
```

For Python:

```text
types.py      primitive/composite/model type mapping
keywords.py   reserved keyword escaping
names.py      class/module/function names
imports.py    import planning
adapter.py    public adapter used by app/adapter/languages.py
```

Language modules should not import from `app`.

Allowed:

```text
app → languages
```

Avoid:

```text
languages → app
```

---

### 9. `src/utils/`

Generic helpers only.

Good examples:

```text
naming
file helpers
template helpers
collection helpers
type helpers
```

If logic is reusable and not domain-specific, put it here.

Do not put Codepot/spec/planning behavior in utils.

---

## Final dependency rule

Keep this topology:

```text
spec/ir  ←  spec/repository  ←  app pipeline  ←  cli
                                  ↑
                              languages
```

And:

```text
utils can be imported by any layer
contracts can be imported by src/languages/emission
spec should not import app or languages
languages should not import app
cli should not import spec internals
```

## Immediate cleanup decision

Use this layout:

```text
src/pipeline/
src/cli/
src/languages/
src/spec/
src/contracts/
src/utils/
```

Do **not** keep duplicate root-level:

```text
cli/
languages/
```

unless your packaging intentionally supports them. Since this is a Python package, keeping importable code under `src/` is simpler.

# Root-level folders

mkdir -p pipeline
mkdir -p templates/python
mkdir -p tests/spec
mkdir -p tests/app
mkdir -p tests/languages

# Pipeline package folders

mkdir -p src/cli/commands
mkdir -p src/cli/constants
mkdir -p src/cli/presentation/core
mkdir -p src/cli/presentation/inspect
mkdir -p src/cli/presentation/validate
mkdir -p src/cli/presentation/infer
mkdir -p src/cli/presentation/emit

mkdir -p src/contracts

mkdir -p src/spec/loader
mkdir -p src/spec/repository
mkdir -p src/spec/ir/shared
mkdir -p src/spec/ir/properties/primitive
mkdir -p src/spec/ir/properties/enum
mkdir -p src/spec/ir/properties/composite
mkdir -p src/spec/ir/schema/entity/field
mkdir -p src/spec/ir/schema/field_set
mkdir -p src/spec/ir/schema/model
mkdir -p src/spec/ir/schema/dto
mkdir -p src/spec/ir/schema/params
mkdir -p src/spec/ir/resource/operation
mkdir -p src/spec/ir/resource/route
mkdir -p src/spec/ir/response/errors
mkdir -p src/spec/ir/security

mkdir -p src/pipeline/selection
mkdir -p src/pipeline/pathing
mkdir -p src/pipeline/planning
mkdir -p src/pipeline/adapter
mkdir -p src/pipeline/emission

mkdir -p src/languages/python

mkdir -p src/utils/naming
mkdir -p src/utils/collections
mkdir -p src/utils/files
mkdir -p src/utils/templates
mkdir -p src/utils/types

# Root files

touch spec.v1.yaml
touch pyproject.toml
touch README.md
touch templates/paths.template.yaml
touch templates/python/enum.py.j2
touch templates/python/model.py.j2
touch templates/python/dto.py.j2
touch templates/python/resource.py.j2
touch templates/python/**init**.py.j2
touch tests/**init**.py
touch tests/conftest.py

# Package root

touch src/**init**.py
touch src/app.py

# CLI

touch src/cli/**init**.py
touch src/cli/main.py
touch src/cli/bootstrap.py
touch src/cli/commands/**init**.py
touch src/cli/commands/inspect.py
touch src/cli/commands/validate.py
touch src/cli/commands/infer.py
touch src/cli/commands/emit.py
touch src/cli/constants/**init**.py
touch src/cli/constants/constants.py
touch src/cli/constants/defaults.py
touch src/cli/presentation/**init**.py
touch src/cli/presentation/core/**init**.py
touch src/cli/presentation/core/console.py
touch src/cli/presentation/core/diagnostics.py
touch src/cli/presentation/core/interactive.py
touch src/cli/presentation/core/tables.py
touch src/cli/presentation/inspect/**init**.py
touch src/cli/presentation/inspect/diagnostics.py
touch src/cli/presentation/inspect/renderer.py
touch src/cli/presentation/inspect/resources.py
touch src/cli/presentation/inspect/status.py
touch src/cli/presentation/inspect/summary.py
touch src/cli/presentation/validate/**init**.py
touch src/cli/presentation/validate/diagnostics.py
touch src/cli/presentation/validate/issues.py
touch src/cli/presentation/validate/renderer.py
touch src/cli/presentation/validate/summary.py
touch src/cli/presentation/infer/**init**.py
touch src/cli/presentation/infer/diagnostics.py
touch src/cli/presentation/infer/files.py
touch src/cli/presentation/infer/renderer.py
touch src/cli/presentation/infer/schemas.py
touch src/cli/presentation/infer/status.py
touch src/cli/presentation/infer/summary.py
touch src/cli/presentation/emit/**init**.py
touch src/cli/presentation/emit/diagnostics.py
touch src/cli/presentation/emit/files.py
touch src/cli/presentation/emit/renderer.py
touch src/cli/presentation/emit/status.py
touch src/cli/presentation/emit/summary.py

# Contracts

touch src/contracts/**init**.py
touch src/contracts/repository.py
touch src/contracts/planning.py
touch src/contracts/language.py
touch src/contracts/paths.py
touch src/contracts/templates.py
touch src/contracts/files.py

# Spec public layer

touch src/spec/**init**.py
touch src/spec/loader/**init**.py
touch src/spec/loader/yaml_loader.py
touch src/spec/repository/**init**.py
touch src/spec/repository/document.py
touch src/spec/repository/records.py
touch src/spec/repository/record_sets.py
touch src/spec/repository/query.py
touch src/spec/repository/refs.py
touch src/spec/repository/graph.py

# Spec IR

touch src/spec/ir/**init**.py

touch src/spec/ir/shared/**init**.py
touch src/spec/ir/shared/ref.py
touch src/spec/ir/shared/base.py
touch src/spec/ir/shared/info.py
touch src/spec/ir/shared/url.py
touch src/spec/ir/shared/content.py
touch src/spec/ir/shared/document.py

touch src/spec/ir/properties/**init**.py
touch src/spec/ir/properties/definition.py
touch src/spec/ir/properties/primitive/**init**.py
touch src/spec/ir/properties/primitive/definition.py
touch src/spec/ir/properties/enum/**init**.py
touch src/spec/ir/properties/enum/definition.py
touch src/spec/ir/properties/composite/**init**.py
touch src/spec/ir/properties/composite/definition.py

touch src/spec/ir/schema/**init**.py
touch src/spec/ir/schema/definition.py
touch src/spec/ir/schema/entity/**init**.py
touch src/spec/ir/schema/entity/definition.py
touch src/spec/ir/schema/entity/field/**init**.py
touch src/spec/ir/schema/entity/field/definition.py
touch src/spec/ir/schema/field_set/**init**.py
touch src/spec/ir/schema/field_set/definition.py
touch src/spec/ir/schema/model/**init**.py
touch src/spec/ir/schema/model/definition.py
touch src/spec/ir/schema/dto/**init**.py
touch src/spec/ir/schema/dto/definition.py
touch src/spec/ir/schema/params/**init**.py
touch src/spec/ir/schema/params/definition.py

touch src/spec/ir/resource/**init**.py
touch src/spec/ir/resource/definition.py
touch src/spec/ir/resource/operation/**init**.py
touch src/spec/ir/resource/operation/definition.py
touch src/spec/ir/resource/route/**init**.py
touch src/spec/ir/resource/route/definition.py

touch src/spec/ir/response/**init**.py
touch src/spec/ir/response/definition.py
touch src/spec/ir/response/errors/**init**.py
touch src/spec/ir/response/errors/definition.py

touch src/spec/ir/security/**init**.py
touch src/spec/ir/security/definition.py

# App orchestration

touch src/pipeline/**init**.py
touch src/pipeline/pipeline.py

touch src/pipeline/selection/**init**.py
touch src/pipeline/selection/kinds.py
touch src/pipeline/selection/config.py
touch src/pipeline/selection/resolver.py

touch src/pipeline/pathing/**init**.py
touch src/pipeline/pathing/identity.py
touch src/pipeline/pathing/branch.py
touch src/pipeline/pathing/variables.py
touch src/pipeline/pathing/planner.py

touch src/pipeline/planning/**init**.py
touch src/pipeline/planning/records.py
touch src/pipeline/planning/pipeline.py

touch src/pipeline/adapter/**init**.py
touch src/pipeline/adapter/languages.py

touch src/pipeline/emission/**init**.py
touch src/pipeline/emission/file_plan.py
touch src/pipeline/emission/renderer.py
touch src/pipeline/emission/writer.py

# Languages

touch src/languages/**init**.py
touch src/languages/contracts.py
touch src/languages/registry.py
touch src/languages/python/**init**.py
touch src/languages/python/adapter.py
touch src/languages/python/names.py
touch src/languages/python/types.py
touch src/languages/python/imports.py
touch src/languages/python/keywords.py

# Utils

touch src/utils/**init**.py
touch src/utils/naming/**init**.py
touch src/utils/naming/aliases.py
touch src/utils/naming/cases.py
touch src/utils/naming/number.py
touch src/utils/naming/plurality.py
touch src/utils/naming/provider.py
touch src/utils/collections/**init**.py
touch src/utils/files/**init**.py
touch src/utils/templates/**init**.py
touch src/utils/types/**init**.py
