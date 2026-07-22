# codepot

> Semantic metadata inference engine + template compiler for generating architecture artifacts from typed domain configs.

---

# What is codepot?

- semantic metadata DSL
- normalized manifest compiler
- inference engine
- template-driven code generator

You define **facts** about your domain.

codepot infers:

- query capabilities
- mutation semantics
- relation groups
- workflows
- validation groups
- reusable template contexts

Templates decide final architecture output.

---

# Core Philosophy

```txt id="8zfr52"
Configs define facts
        ↓
Inference engine derives semantics
        ↓
Normalized context is generated
        ↓
codepot templates render output
```

codepot does **not** hardcode:

- NestJS
- TypeORM
- FastAPI
- GraphQL
- React
- REST
- DTO patterns
- folder structures

All architecture styles are implemented through templates.

---

# Features

- Strongly typed TypeScript configs
- Semantic metadata inference
- codepot-based generation
- Framework agnostic
- Runtime metadata compilation
- Query/mutation capability inference
- Typed enum transitions/workflows
- Semantic validation rule AST
- Relation graph inference
- JSON-safe normalized manifests
- Extensible template ecosystem

---

# Example Use Cases

Generate:

- DTOs
- ORM entities
- repositories
- GraphQL schemas
- Zod schemas
- Pydantic models
- React forms
- OpenAPI specs
- validation layers
- constants
- metadata registries
- query builders
- admin panels
- SDKs

from a single semantic source of truth.

---

# Installation

```bash
npm install codepot
```

---

# Quick Example

## Entity Config

```ts
import {
  EntityConfigBase,
  stringField,
  enumField,
  query,
  mutation,
  transition,
} from "codepot";

export default class UserEntityConfig extends EntityConfigBase {
  key = "user";

  fields = this.defineFields({
    email: stringField({
      length: 255,

      query: query().select().defaultSelect().search().sort().build(),

      mutation: mutation().apiWritable().build(),
    }),

    status: enumField(["active", "suspended", "deleted"] as const, {
      default: "active",
    }),
  });

  transitions = [
    transition({
      field: () => this.fields.status,

      initial: this.fields.status.values.active,

      terminal: [this.fields.status.values.deleted],

      transitions: {
        [this.fields.status.values.active]: [
          this.fields.status.values.suspended,
          this.fields.status.values.deleted,
        ],

        [this.fields.status.values.suspended]: [
          this.fields.status.values.active,
          this.fields.status.values.deleted,
        ],

        [this.fields.status.values.deleted]: [],
      },
    }),
  ];

  templates = [
    "dto.create",
    "dto.update",
    "typeorm.entity",
    "schema.zod",
  ] as const;
}
```

---

# Semantic Inference

codepot automatically infers semantic groups from metadata.

You never manually define groups.

For example:

```ts
query().select().defaultSelect().search().build();
```

automatically contributes the field into:

```txt id="i0j75l"
entity.fields.query.select
entity.fields.query.default_select
entity.fields.query.search
```

Likewise:

```ts
mutation().apiWritable().immutableAfterCreate().build();
```

automatically contributes the field into:

```txt id="vs7rmi"
entity.fields.mutation.api_create
entity.fields.mutation.immutable_after_create
```

---

# codepot Templates

codepot uses codepot for rendering generated artifacts.

Templates receive a normalized semantic context.

---

# Example Template

## `dto.create.codepot`

```codepot
export class Create{{entity.pascal_case_key}}Dto {
{{#each entity.fields.mutation.api_create}}
  {{snake_case_key}}!:
  {{typescript_type}};
{{/each}}
}
```

---

# Example Generated Output

```ts
export class CreateUserDto {
  email!: string;
  status!: UserStatus;
}
```

---

# Template Context

All exposed template variables are normalized to `snake_case`.

Example context:

```json
{
  "entity": {
    "key": "user",

    "pascal_case_key": "User",

    "fields": {
      "all": [],

      "strings": [],

      "enums": [],

      "query": {
        "select": [],
        "default_select": [],
        "search": [],
        "sort": []
      },

      "mutation": {
        "api_create": [],
        "api_update": [],
        "immutable": [],
        "generated": []
      }
    },

    "relations": {
      "all": []
    },

    "checks": {
      "all": []
    },

    "indexes": {
      "all": []
    }
  }
}
```

---

# Query Builder

Semantic query capabilities are defined fluently.

```ts
query().select().defaultSelect().sort().search().build();
```

---

# Mutation Builder

Mutation semantics describe API/system behavior.

```ts
mutation().apiWritable().immutableAfterCreate().build();
```

Supported semantics include:

- api writable
- system writable
- readonly
- immutable
- immutable after create
- generated
- computed
- persisted

---

# Relations

Relations are fully typed semantic metadata.

```ts
relationField(this, AppEntityConfig, {
  relation: {
    kind: "one_to_many",

    remote_field: () => new AppEntityConfig().fields.ownerId,

    cascade: true,
  },

  query: {
    select: true,
  },
});
```

---

# Semantic Validation Rules

Checks are represented as semantic ASTs.

No raw SQL.

```ts
checks = [
  {
    name: "email_not_empty",

    rule: field(() => this.fields.email).notEmpty(),
  },
];
```

---

# Workflows / Transitions

Transitions are defined independently from enum fields.

```ts
transition({
  field: () => this.fields.status,

  initial: this.fields.status.values.active,

  terminal: [this.fields.status.values.deleted],

  transitions: {
    active: ["suspended", "deleted"],
    suspended: ["active", "deleted"],
    deleted: [],
  },
});
```

---

# Compiler Pipeline

```txt id="urvq4h"
TypeScript Configs
        ↓
Runtime Metadata Extraction
        ↓
Semantic Inference Engine
        ↓
Normalized Manifest
        ↓
codepot Template Compilation
        ↓
Generated Source Code
```

---

# Design Goals

## codepot SHOULD:

- infer semantic groups automatically
- remain architecture agnostic
- support multiple output ecosystems
- expose normalized template context
- prioritize metadata semantics over implementation details

## codepot SHOULD NOT:

- hardcode framework architecture
- assume NestJS patterns
- assume ORM implementations
- force a specific folder structure
- expose raw database concerns directly

---

# Long-Term Vision

codepot aims to become a universal semantic metadata compiler capable of generating:

- backend architectures
- frontend forms
- APIs
- SDKs
- validation layers
- schemas
- admin systems
- documentation
- infrastructure metadata

from a single semantic domain definition.

---

# Example Future Ecosystem

```txt id="phl2a6"
codepot
@codepot/compiler
@codepot/runtime
@codepot/templates
@codepot/typeorm
@codepot/graphql
@codepot/zod
@codepot/react-form
@codepot/openapi
@codepot/fastapi
```

---

# License

MIT
