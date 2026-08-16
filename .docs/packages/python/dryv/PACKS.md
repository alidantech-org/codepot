# Dryv Pack contract

A Dryv pack defines how Canonical Runtime IR becomes planned generated artifacts. Pack metadata remains language/runtime neutral; emitted syntax remains entirely inside template resources.

## Manifest

The active manifest is `dryv.pack.yaml` with schema `dryv.dev/v1`.

The implemented root vocabulary is:

```text
apiVersion
id
version
description
options
bindings
selections
templates
requires
executables
commands
```

Unknown fields are rejected.

## Selection vocabulary

A selection chooses one canonical IR kind. The current closed vocabulary is:

```text
contract
group
property
schema
policy
failure
event
operation
storage_mapping
value_source
view
workflow
presentation
```

A selection has a stable key and may declare the binding names and symbolic names it exposes to its templates.

Example:

```yaml
selections:
  schemas:
    kind: schema
    bindings: []
    symbols: []
```

Clients do not send `PlanningCandidate` objects. Runtime derives invocations from Canonical IR plus the pack manifest.

## Template declarations

Every template is declared by the pack itself:

```yaml
templates:
  schema-type:
    selection: schemas
    file: templates/schema.ts.j2
    renderer: jinja
    output: src/models/{pascal}.ts
    dependsOn: []
```

A declaration owns:

- template key;
- selection key;
- pack-relative template file;
- required renderer capability;
- deterministic output pattern;
- dependencies on other template declarations.

The API must never reconstruct this mapping itself.

## Output placeholders

The current output placeholder vocabulary is intentionally closed:

```text
{name}
{singular}
{plural}
{snake}
{kebab}
{camel}
{pascal}
{kind}
```

Runtime resolves the pattern against the selected semantic subject and prefixes the configured pack output root from `dryv.yaml`. Resulting artifact paths must remain normalized project-relative POSIX paths.

## Pack bundles and logical resources

Project Clients resolve local/Git pack sources before calling a remote API. The build carries an explicit pack bundle:

```text
instance name
manifest logical resource id
pack-relative path -> logical resource id
```

Runtime never traverses the user's filesystem and never clones a repository.

The manifest decides which bundled resource is a template. Runtime verifies that every referenced template exists and records the resource media type and content hash in the `GenerationPlan`.

## Options and bindings

Options are pack-owned public configuration with deterministic defaults, choices and required checks.

Bindings are project-provided explicit values. A pack may state which selections consume them. Unknown options/bindings and missing required values are errors.

## Template dependencies

`dependsOn` names another template declaration in the same pack instance. Planning resolves the corresponding render-job dependency against the same semantic subject or one of that subject's canonical semantic dependencies.

The final plan therefore contains artifact dependencies before rendering starts. Cycles and unresolved required template dependencies are errors.

## Context ownership

Runtime owns template context meaning. A Render Client receives JSON-compatible context, never Canonical IR Python objects.

The current context includes:

```text
project
subject / subjectId / subjectKind
effective                    # for Schema when applicable
semantic dependencies
current planned artifact
dependency planned artifacts
pack id / instance / version
pack options / bindings
selection key / symbols
```

Each job also carries a context hash and a context contract containing the available JSON paths plus a contract hash. `dryv-api` later uses this for renderer preflight without understanding pack semantics.

## GenerationPlan boundary

Planning produces:

```text
stable RenderJob identity
deterministic order
semantic subject identity/kind
selection reason
renderer capability requirement
template resource identity/hash/media type
canonical context/context contract/hashes
planned artifact id/path
semantic dependencies
render-job/artifact dependencies
pack hashes
plan hash
```

Dryv Engine stops there.

## What packs do not own

Packs do not:

- redefine Canonical IR concepts;
- connect to Render Clients;
- write project files;
- execute template engines;
- manage Git credentials;
- choose renderer network endpoints;
- create ZIP bundles;
- mutate server/client filesystem state;
- embed framework-specific syntax into Canonical IR.
