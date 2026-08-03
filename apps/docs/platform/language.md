---
title: Codepot Lang
description: The strongly typed semantic application language implemented in Rust at the center of the final Codepot platform.
product: codepot-lang
order: 21
---

# Codepot Lang

Codepot Lang is a strongly typed semantic application language implemented in Rust.

It models world meaning, software intent, contracts, APIs, screens, workflows, security, and reusable project foundations without embedding TypeScript, SQL, ORM, or UI-framework syntax in application source.

## Current version

The active repository documents language version **0.3**.

Supported source extensions are:

```text
.pot
.code
.codepot
.cpt
```

Module identity comes from the filesystem and `Codepot.toml`; source files do not declare packages.

## Example

```codepot
from app.foundation.state import SoftDeletableEntity;
from std.core import Bool, Text;
from std.software.contract import Input, Output;
from std.software.state import Entity;
from std.world.identity import Email, Name, Username;

/**
 * Application user account.
 *
 * @security Public projections must never include secret fields.
 */
Entity User extends SoftDeletableEntity {
  name: Name required() max(120)
  username: Username required() unique()
  email: Email required() unique()
  active: Bool required() default(true)
  biography: Text optional() max(1000)
}

Input UpdateUser from User {
  use partial(ref(User)) {
    name
    username
    email
    biography
  }
}

Output UserResponse {
  user: ref(User).public()
}
```

## Language principles

- Only `from <module> import ...` imports exist.
- Wildcard imports require a namespace alias.
- `std.core` is the small implicit prelude; other dependencies remain explicit.
- The language is strongly and statically typed.
- Generic arity, receivers, arguments, references, inheritance, projections, and rule changes are validated before IR.
- Standard values such as `Email`, `Slug`, `Username`, `Phone`, and `Url` carry reusable default rules.
- A use can refine an inherited rule or remove it explicitly with `without("ruleName")`.
- `ref()` creates a semantic usage without blindly copying storage-only behavior.
- The Rust formatter is canonical for both CLI and language server.

## Constructs come from the standard library

The parser does not hardcode names such as `Entity`, `Input`, `Api`, or `Screen` as grammar keywords.

They are standard-library constructs resolved by semantic analysis. This lets the language keep a small kernel while software categories evolve through typed libraries.

## Documentation and tools

Ordinary comments are preserved for formatting but excluded from semantic analysis. Documentation comments attach to declarations, fields, operations, known values, and rules.

Documentation is retained in AST and IR and surfaced by hover, completion, and signature help.

## Current output

Version 0.3 produces:

- an in-memory semantic program;
- target-neutral IR;
- optional deterministic YAML.

Runtime loops, async execution, exceptions, filesystem access, network access, a final interpreter, and complete deterministic code generation are not yet described as finished language features.

## Project configuration

```toml
[project]
name = "my-codepot-project"
language-version = "0.3"

[packages]
app = "src/app"
vendor = "vendor"

[standard-library]
mode = "embedded"

[compiler]
entry = "src/app/main.codepot"
output = ".codepot/app.ir.yaml"
```

## Relationship to the wider ecosystem

The prototype packages prove contract and generation behavior. `codepotx` stabilizes runtime and artifact boundaries. Codepot Lang gives those mature ideas a purpose-built language and compiler foundation.
