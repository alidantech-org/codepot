# Authoring architecture

## Responsibility

`codepotg-author` is a trusted executable Python frontend that compiles concise typed declarations into the public immutable `codepotg.ir.Contract`.

It is not a Codepot plugin that extends semantics. It does not own generation, selection, rendering, writing, commands, or target implementation.

## Dependency direction

```text
codepotg-core
    ↑
codepotg-author
    ├── Pydantic author models
    ├── typed refs and registries
    ├── author compiler
    └── canonical IR transport
```

Core never imports Pydantic or the author package.

## One semantic model

Authoring declarations are temporary compiler input. The only semantic output is core IR. After compilation:

- Pydantic classes are absent;
- Python functions and lambdas are absent;
- builder objects are absent;
- author refs are replaced by semantic IDs;
- mutable registries are absent;
- all collections are immutable and deterministic.

## Explicit author session

All declarations belong to an explicit `Author` instance. Decorators may register only with that instance.

```python
author = cp.Author(id="defytickets", name="DefyTickets", version="1.0.0")
users = author.group("users")

@users.schema("User")
class UserModel(BaseModel):
    ...
```

There is no process-global decorator, ref, schema, or compilation registry.

## Trust boundary

Python author files are trusted executable build code. The package itself must still avoid automatic network access, filesystem scanning, environment reading, command execution, and import-time compilation.

## Public surfaces

Planned public API families:

```text
codepotg_author.Author
codepotg_author.Model
codepotg_author.field / constraints / tags / info
codepotg_author.refs.*
codepotg_author.operations.*
codepotg_author.facets.*
codepotg_author.transport.*
codepotg_author.result.AuthoringResult
```

Public APIs are added only with matching typing, runtime validation, diagnostics, documentation, and tests.

## Core evolution rule

Tags, categorized guidance, connected field capabilities, value sources, presentations, or expanded HTTP facts may enter compiled output only after core publishes typed versions. Until then:

- author declarations may be designed and tested in isolation;
- compilation of unsupported declarations returns an exact blocker diagnostic;
- nothing is hidden in `extensions`, `raw`, or private author IR;
- core files are not modified by package implementation agents unless a separate approved core task explicitly grants ownership.
