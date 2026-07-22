---
title: Context Validation
description: Validating context data in Codepurify
---

# Context Validation

Ensure context data meets expected schemas and constraints.

## Validation Schema

```typescript
import { z } from 'zod';

const EntitySchema = z.object({
  names: z.object({
    original: z.string(),
    casing: z.object({
      camel: z.string(),
      pascal: z.string(),
      snake: z.string(),
      kebab: z.string()
    })
  }),
  fields: z.object({
    arrays: z.object({
      all: z.object({
        items: z.array(FieldSchema),
        length: z.number()
      })
    })
  })
});

const FieldSchema = z.object({
  names: z.object({
    original: z.string(),
    casing: z.object({
      camel: z.string(),
      pascal: z.string()
    })
  }),
  flags: z.object({
    is_string: z.boolean(),
    is_number: z.boolean(),
    is_nullable: z.boolean(),
    is_required: z.boolean()
  })
});
```

## Validation Middleware

```typescript
import { ValidationMiddleware } from '@codepurify/core';

class ContextValidator extends ValidationMiddleware {
  validate(context: Context): ValidationResult {
    try {
      EntitySchema.parse(context.entity);
      return { valid: true };
    } catch (error) {
      return { 
        valid: false, 
        errors: error.errors 
      };
    }
  }
}
```

## Custom Validators

```typescript
class CustomValidator {
  validateFieldNaming(field: Field): boolean {
    // Ensure field names follow conventions
    return /^[a-z][a-zA-Z0-9]*$/.test(field.names.original);
  }
  
  validateRelationType(relation: Relation): boolean {
    const validTypes = ['one-to-one', 'one-to-many', 'many-to-one', 'many-to-many'];
    return validTypes.includes(relation.kind);
  }
}
```

## Error Handling

```typescript
interface ValidationResult {
  valid: boolean;
  errors?: ValidationError[];
}

interface ValidationError {
  path: string;
  message: string;
  code: string;
}
```

## Runtime Validation

```typescript
app.use((context, next) => {
  const validation = validator.validate(context);
  
  if (!validation.valid) {
    throw new ValidationError(validation.errors);
  }
  
  return next();
});
```
