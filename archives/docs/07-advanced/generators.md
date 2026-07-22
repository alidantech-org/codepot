---
title: Custom Generators
description: Building custom code generators for Codepurify
---

# Custom Generators

Create custom generators to extend Codepurify's capabilities.

## Generator Structure

```typescript
import { Generator, Context, Output } from "@codepurify/core";

export class CustomGenerator implements Generator {
  name = "custom-generator";

  async generate(context: Context): Promise<Output[]> {
    const outputs: Output[] = [];

    // Generate files based on context
    outputs.push({
      path: `${context.entity.names.kebab}.ts`,
      content: this.generateContent(context),
    });

    return outputs;
  }

  private generateContent(context: Context): string {
    return `export class ${context.entity.names.casing.pascal} {
      // Generated content
    }`;
  }
}
```

## Registration

```typescript
import { Codepurify } from "@codepurify/core";
import { CustomGenerator } from "./generators/custom";

const app = new Codepurify();
app.registerGenerator(new CustomGenerator());
```

## Context Access

Generators receive full context access:

```typescript
async generate(context: Context): Promise<Output[]> {
  const entity = context.entity;
  const fields = entity.fields.arrays.all.items;

  return fields.map(field => ({
    path: `${field.names.kebab}.ts`,
    content: this.generateFieldFile(field)
  }));
}
```

## Output Types

```typescript
interface Output {
  path: string;
  content: string;
  encoding?: "utf-8" | "binary";
}
```

## Async Operations

Generators support async operations:

```typescript
async generate(context: Context): Promise<Output[]> {
  const outputs: Output[] = [];

  // Read external files
  const template = await fs.readFile('template.codepurify', 'utf-8');

  // Process with external APIs
  const processed = await this.processWithAPI(context);

  outputs.push({
    path: 'output.ts',
    content: processed
  });

  return outputs;
}
```
