# Dryv Pack contract

A Dryv pack defines how Canonical Runtime IR becomes planned generated artifacts. Pack metadata remains language/runtime neutral; all target syntax stays in template resources.

## Manifest

The active pack manifest is `dryv.pack.yaml` with versioned schema `dryv.dev/v1`.

Approved root concerns include:

```text
apiVersion
id / version / description
requires
include / exclude
options
bindings
selections
executables
commands
```

Unknown fields are rejected rather than becoming hidden generator behavior.

## Logical resources

The Runtime never clones or traverses arbitrary pack paths. The Project Client/API supplies explicit logical resources:

```text
manifest resource id
logical template resource id
media type
content bytes/hash
required renderer capability
optional approved selection relationship
```

A build is rejected when a referenced manifest/template resource is absent from the Resource inventory.

## Options and bindings

Options are pack-owned public configuration with deterministic defaults/choices/required checks.

Bindings are explicit project-provided values. A selection states which bindings it consumes. Bindings do not authorize arbitrary environment/project filesystem reads by Runtime or templates.

## Selections

Selections remain the explicit generation registry. Approved existing vocabulary such as group-rooted semantic selectors may be used where already defined by the canonical pack specification.

This migration intentionally did not expand unresolved user-facing vocabulary for filtering/grouping/import/export/symbol behavior. Runtime/API therefore accepts an explicit normalized `PlanningCandidate` contract for the generation facts needed by Planning.

That is not permission for clients to invent semantic meaning: Runtime validates candidate pack/template/selection references, and semantic dependencies/context remain inspectable. Future approved selection vocabulary can move more candidate derivation into Planning without changing Render/Artifact/API contracts.

## Planning boundary

Planning turns validated semantic facts + normalized pack declarations + resolved usage inputs into:

```text
selected semantic subject(s)
template invocation
skip reason when skipped
canonical JSON context
semantic dependency set
required renderer capability
virtual artifact id/path
artifact dependency set
trace/provenance
```

Virtual artifacts exist before files exist. A dependent invocation can use planned artifact/path facts without waiting for a Project Client write.

## Template context

Render Clients receive only bounded JSON-compatible context prepared by Planning. They do not receive Python objects, callbacks, lazy semantic resolvers, or an unbounded Contract.

Planning records which semantic IDs/branches contributed to each context so Hashing/Cache can invalidate narrowly.

## Renderer capability

Renderer requirement is an explicit template/resource inventory fact, e.g.:

```text
jinja/v1
handlebars/v1
```

Runtime Scheduling selects among established sessions that advertise the required capability. A pack does not discover/install an in-process template engine.

## Artifact relationship

Planning declares logical outputs and project-relative paths. Templating validates that a Render Client returns only those planned logical output IDs. Artifacts then classify safe Project Client instructions.

## Explainability

The build trace preserves enough provenance to answer:

```text
which pack declaration/template caused this invocation?
which semantic subject(s) caused it?
why was it selected or skipped?
which context/dependencies were consumed?
which renderer session handled it?
which artifact/path resulted?
why is the local instruction create/update/unchanged/delete-managed?
```

## What packs do not own

Packs do not:

- redefine Canonical IR concepts;
- write project files;
- execute template engines;
- manage Git credentials/repository acquisition;
- host renderer processes;
- mutate cache storage directly;
- embed framework meaning into IR.
