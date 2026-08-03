# CodepotG configuration schemas

CodepotG ships Draft 2020-12 JSON Schemas for its two YAML authoring files:

```text
Codepotg.yaml / Codepotg.yml
paths.yaml / paths.yml
```

The schema files live in the installed Python package under:

```text
codepotg/schemas/codepotg.schema.json
codepotg/schemas/paths.schema.json
```

Their canonical deployment identifiers are:

```text
https://schemas.codepot.dev/codepotg/v1/codepotg.schema.json
https://schemas.codepot.dev/codepotg/v1/paths.schema.json
```

These identifiers are stored in the repository now and can be deployed later without changing authored configuration files.

## Link `Codepotg.yaml`

Use both the YAML language-server modeline and the typed `$schema` field:

```yaml
# yaml-language-server: $schema=https://schemas.codepot.dev/codepotg/v1/codepotg.schema.json
$schema: https://schemas.codepot.dev/codepotg/v1/codepotg.schema.json

allow: true

tasks:
  client:
    input: ./openapi.json
    language: python
    templateDir: ./templates
    output: ./generated
```

CodepotG retains the `$schema` value as `CodepotFile.schema_uri`. It does not affect path resolution or generation.

A complete example is available at [`examples/Codepotg.yaml`](examples/Codepotg.yaml).

## Link `paths.yaml`

```yaml
# yaml-language-server: $schema=https://schemas.codepot.dev/codepotg/v1/paths.schema.json
$schema: https://schemas.codepot.dev/codepotg/v1/paths.schema.json

template_extension: .j2
strip_template_extension: true
allow_raw_files: false

selections:
  models:
    select: schemas.emit_models
    as: model
    scope: each

emissions:
  model-files:
    selection: models
    template: model.py.j2
    output: [generated, models, "[model.emit.file_name]"]
```

CodepotG retains this value as `PathConfig.schema_uri`. Strict loading removes only `$schema` before validating the typed `paths.yaml` contract, so unrelated unknown keys are still rejected.

A complete graph example is available at [`examples/paths.yaml`](examples/paths.yaml).

## Python access

Tools that need to inspect or publish the bundled schemas can use:

```python
from codepotg.schemas import load_schema, schema_path

codepotg_schema = load_schema("codepotg")
paths_schema_path = schema_path("paths")
```

Supported names are:

```text
codepotg
paths
```

## Schema responsibilities

The `Codepotg.yaml` schema covers:

- the explicit `allow` safety flag;
- shared task defaults;
- named generation tasks;
- input, output, language, templates, and frontend selection;
- clean paths;
- before and after commands;
- command working directories, optional behavior, and environment values.

The `paths.yaml` schema covers:

- template extension behavior;
- raw-file handling;
- import strategy;
- managed and immutable write roots;
- legacy folder recipes;
- named selections and scopes;
- emissions, providers, and capabilities;
- barrels and lifecycle modes;
- author metadata.

Runtime validation remains authoritative for cross-reference rules that JSON Schema cannot fully express, including provider existence, selection references, barrel export references, duplicate aliases, and dependency cycles.

## Compatibility

The `$schema` field is optional. Existing files without it continue to load unchanged.

Both supported filename variants remain valid:

```text
Codepotg.yaml
Codepotg.yml

paths.yaml
paths.yml
```
