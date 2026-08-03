# codepot

TypeScript-first OpenAPI contract engine for building strongly typed, SDK-ready API contracts.

CodePot lets you define API contracts using **typed builders instead of raw OpenAPI YAML**, then compiles them into OpenAPI 3.1 + rich SDK metadata.

---

# Core idea

You define **contract-level facts in code**, and CodePot generates:

- OpenAPI 3.1 documents
- SDK-friendly metadata (`x-codegen-*`)
- reusable schema components
- validated and deduplicated refs

```txt
Contract (TypeScript DSL)
        ↓
Compiler pipeline
        ↓
Normalized IR
        ↓
OpenAPI + SDK metadata output
```

---

# Features

- TypeScript-first contract DSL
- Strongly typed resources, schemas, and routes
- Reusable property system (shared, entity, ref)
- Automatic OpenAPI 3.1 generation
- Ref-safe compilation (no duplicate schema drift)
- SDK metadata inference (`x-codegen-*`)
- Default responses system
- Query capability inference per field
- Entity inheritance support
- OpenAPI component bucketing (schemas / params / responses / requests)

---

# Installation

```bash
pnpm add -D codepot
```

Peer dependency:

```bash
pnpm add zod
```

---

# Quick start

## 1. Create config

```ts
import { definePackageConfig } from 'codepot';

export default definePackageConfig({
  contracts: [],
  output: {
    folder: 'openapi',
    formats: ['json', 'yaml'],
  },
});
```

---

## 2. Define a version contract

```ts
import { defineVersionContract } from 'codepot';

const v1 = defineVersionContract({
  info: {
    title: 'My API',
    version: 'v1',
    description: 'Core API',
  },
});
```

---

## 3. Define a resource

```ts
const users = v1.defineResource({
  key: 'users',
  name: 'User',
  basePath: '/users',
});
```

---

## 4. Define routes

```ts
users.defineRoutes({
  routes: {
    listUsers: {
      method: 'get',
      path: '/',
      responses: {
        200: userResponses.ref.UsersListOkResponse,
      },
    },
  },
});
```

---

## 5. Generate OpenAPI

```bash
codepot generate
```

Output:

```txt
openapi/openapi.v1.json
openapi/openapi.v1.yaml
```

---

# Core concepts

## Contracts

A contract is a full API version:

```ts
const v1 = defineVersionContract(...)
```

---

## Resources

A resource groups endpoints:

```ts
defineResource({
  key: 'users',
  basePath: '/users',
});
```

---

## Properties

Properties define reusable field primitives.

- `shared()` → global primitives
- `entity()` → domain models
- `forRef()` → reusable refs

---

## Entities

Entities are model definitions with:

- public model
- selected model
- partial model
- query model inference
- inheritance support

---

## Routes

Routes define HTTP operations:

```ts
method;
path;
query;
body;
responses;
```

---

## Components

Auto-generated OpenAPI components:

- schemas
- parameters
- requestBodies
- responses

---

## SDK metadata

CodePot emits metadata:

```yaml
x-codegen-kind: dto | enum | primitive
x-codegen-group
x-codegen-operation
x-codegen-inherits
```

---

# Output

Generated files:

```txt
openapi/
  openapi.v1.json
  openapi.v1.yaml
  contract-debug.v1.json
```

---

# Architecture pipeline

```txt
Contract DSL
   ↓
IR normalization
   ↓
Validation layer
   ↓
Compilation layer
   ↓
OpenAPI target writer
```

---

# Design goals

- No manual OpenAPI writing
- No duplicated schema definitions
- Fully typed contract system
- SDK-first output design
- Strict separation of:
  - contract
  - pipeline
  - utils

---

# CLI

```bash
codepot init
codepot generate
codepot validate
```

---

# Status

Early-stage but stable core compiler + contract system.

---

# License

MIT
