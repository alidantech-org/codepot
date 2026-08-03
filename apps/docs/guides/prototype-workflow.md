---
title: Prototype workflow
description: Build a typed OpenAPI contract with codepot-openapi and generate project code with CodepotG and Jinja.
order: 41
---

# Prototype workflow

This guide uses the supported production-used workflow:

```text
codepot-openapi → OpenAPI + x-codegen → codepotg → Jinja pack → project files
```

## 1. Install

```bash
npm install codepot-openapi zod
python -m pip install codepotg
```

## 2. Author a contract

```ts
import {
  definePackageConfig,
  defineVersionContract,
} from 'codepot-openapi';
import { z } from 'zod';

const v1 = defineVersionContract({
  info: { title: 'Example API', version: 'v1' },
});

const users = v1.defineResource({
  name: 'users',
  route: '/users',
});

const schemas = users.defineSchemas({
  User: {
    id: z.string().uuid(),
    email: z.string().email(),
  },
}).ref;

users.defineRoutes().routes((route) => ({
  listUsers: route.get('/').response(schemas.User.array()),
}));

export default definePackageConfig({
  contracts: [v1],
  output: {
    folder: '.',
    filePrefix: 'openapi',
    formats: ['json', 'yaml'],
  },
});
```

## 3. Generate OpenAPI

```bash
npx codepot-openapi generate
```

Confirm that the configured JSON or YAML file exists and contains standard OpenAPI fields.

## 4. Create `Codepotg.yaml`

```yaml
allow: true

tasks:
  sdk:
    input: ./openapi.json
    language: typescript
    output: ./generated/sdk
```

When `templateDir` is absent, CodepotG uses the bundled pack for `language`.

## 5. Preview

```bash
codepotg generate sdk --dry-run --verbose
```

Review planned files, diagnostics, lifecycle classification, and commands before allowing writes.

## 6. Generate

```bash
codepotg generate sdk
```

## 7. Use a custom Jinja pack

```yaml
allow: true

tasks:
  sdk:
    input: ./openapi.json
    language: typescript
    templateDir: ./templates/typescript
    output: ./generated/sdk
```

Keep `paths.yaml`, partials, filters, and templates under the selected directory.

## 8. Configure lifecycle policy

Use managed roots for refreshable output and immutable roots for create-once scaffolds.

```yaml
write_policy:
  default_mode: managed
  managed_roots: [generated]
  immutable_roots: [src]
  protected_roots: [src/manual]
  clean_roots: [generated]
```

Do not use broad cleanup to delete user-owned files.

## 9. Add commands carefully

Before and after commands are project-owned executable behavior. Review them before enabling a new pack or repository task.

Use `--skip-before` and `--skip-after` while diagnosing generation.
