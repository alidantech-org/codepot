# Public Python API

## Primary product interface

The Python API is the primary CodepotG v2 interface. CLI, MCP, HTTP, playground, notebook, IDE, and future blast-radius UI integrations call the same application services.

Generation logic never depends on terminal arguments, printing, process exit, or current working directory.

## Supported facade

```python
from codepotg import CodepotG

runtime = CodepotG.standard()
```

Hosts may construct explicit immutable compositions:

```python
runtime = CodepotG.create(
    plugin_registry=registry,
    pack_provider=provider,
    artifact_writer=writer,
    security_policy=policy,
    cache=cache,
)
```

Composition selects adapters/infrastructure. It does not replace or extend the closed semantic kernel, selector registry, expression contract, or template-context types.

## Core operations

Synchronous and asynchronous operations include:

- configure a project or pack instance;
- validate project/pack configuration and closed semantic input;
- inspect installed adapters and typed option schemas;
- inspect a pack contract and filesystem descriptors;
- resolve local/Git packs and locks;
- compile and inspect a complete semantic/artifact plan;
- explain one artifact or declared symbol;
- query impact/blast radius from a semantic item or proposed change;
- dry-run create/change/delete/leave decisions;
- generate to memory, filesystem, or archive;
- inspect unresolved bindings, commands, approvals, and readiness actions;
- inspect cache, ownership/generation state, and lock state.

Request objects are preferred:

```python
result = runtime.generate(
    GenerationRequest.from_project_file("codepotg.yaml")
)
```

Programmatic callers can construct typed requests without YAML:

```python
request = GenerationRequest(
    project=ProjectConfig(...),
    selected_packs=("server",),
    output_mode=OutputMode.MEMORY,
)
```

Programmatic construction still uses the fixed public kernel/configuration types. Callers cannot register arbitrary semantic nodes, facets, selectors, or context properties.

## Sessions

Each operation creates an isolated session containing:

- request/session identity;
- cancellation token and runtime event sink;
- diagnostics;
- loaded source documents;
- normalized immutable closed-kernel IR;
- private typed relationship indexes;
- resolved packs/adapters and behavior identities;
- effective typed options/bindings;
- root-first selector instances;
- complete artifact/dependency/export/path graph;
- explain/impact graph;
- staged artifacts;
- command approvals;
- ownership/generation-state and cache scope.

A reusable runtime may serve concurrent requests, but session state never leaks.

## Results

Expected validation/planning failures return structured results rather than generic exceptions.

```text
ConfigureResult
ValidationResult
InspectionResult
PlanResult
ExplainResult
ImpactResult
GenerationResult
PackResolutionResult
ApprovalResult
StateResult
```

Every result contains:

- status;
- deterministic diagnostics;
- operation-specific typed data;
- runtime events or summary;
- readiness/manual actions where applicable;
- reproducibility identities;
- stable serialization for CLI/MCP/HTTP/IDE boundaries.

Unexpected programming/infrastructure failures may raise typed exceptions at the API boundary after diagnostic conversion where possible.

## Plan, explain, and impact

`plan` compiles the complete semantic and artifact plan without writing.

`explain` traces an artifact/symbol through:

```text
source provenance and semantic identity
→ fixed selector and active scope
→ template/static descriptor
→ options/bindings/generated dependencies
→ declared symbols and destination
```

`impact` uses the same plan to report:

```text
changed semantic item/relation
→ affected selections
→ affected invocations
→ affected provider/consumer/barrel artifacts
```

Initial guarantees are artifact- and symbol-level. Exact generated-line source maps require explicit future engine support and are not fabricated by the API.

## Status

Generation/readiness statuses may include:

```text
ready
generated_with_warnings
generated_with_actions
partially_generated
failed
cancelled
```

Fragment or integration packs may produce useful output while reporting unresolved bindings/manual actions when project policy permits it.

## In-memory operation

```python
result = runtime.generate(
    GenerationRequest(..., output_mode=OutputMode.MEMORY)
)

for artifact in result.artifacts:
    print(artifact.path, artifact.content)
```

Writers are ports, so the same valid plan can target:

- transactional filesystem output;
- memory;
- archive;
- controlled future stores.

Templates never receive writer handles or host filesystem authority.

## Runtime events

Runtime progress events are distinct from application semantic `group.events`:

```text
ConfigurationLoaded
PackResolved
AdapterResolved
SourceLoaded
NormalizationStarted
NormalizationCompleted
SemanticValidated
PlanCompiled
ImpactCalculated
ArtifactStarted
ArtifactCompleted
CommandApprovalRequired
TransactionCommitted
OperationFailed
```

Frontends format/stream runtime events independently.

## Async behavior

Async operations support cancellation, host deadlines, controlled remote pack/reference retrieval, event streaming, asynchronous writers/stores, and approved subprocess execution.

Sync and async APIs use the same application services and must not hide cancellation or create unsafe nested loops.

## Server-safe defaults

`SecurityPolicy.server_safe()` denies:

- project/pack commands and shell execution;
- network except explicitly authorized providers/loaders;
- environment inheritance;
- filesystem access outside declared inputs/staging;
- template access to filesystem/network/environment/processes;
- plugin semantic-kernel mutation.

A project, pack, or adapter cannot weaken host policy.

## Public namespace policy

Stable public modules may include:

```text
codepotg.api
codepotg.config
codepotg.ir
codepotg.generation
codepotg.plugins
codepotg.ports
codepotg.diagnostics
codepotg.testing
```

Private graph/index builders and implementation modules are not extension points. No public generic semantic registration or target source-renderer API exists.
