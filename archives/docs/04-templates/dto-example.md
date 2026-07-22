---
title: DTO Example
description: Complete Create DTO template with real-world usage
---

# DTO Example

Generate a Create DTO with validation decorators.

## Template File

`templates/create-user.dto.codepurify`:

```codepurify
import { IsString, IsEmail, IsOptional, IsNumber, Min, Max } from
'class-validator'; export class Create{| entity.names.casing.pascal |}DTO {
{|#each entity.fields.arrays.all.items as field|} {|#if field.flags.is_primary|}
// Primary key excluded from create DTO {|else if field.flags.is_string|} {|#if
field.flags.is_nullable|} @IsOptional() {|/if|} {|#if field.flags.is_email|}
@IsEmail() {|else|} @IsString() {|/if|} {|field.names.casing.camel|}: {|#if
field.flags.is_nullable|}string | null{|else|}string{|/if|}; {|else if
field.flags.is_number|} {|#if field.flags.is_nullable|} @IsOptional() {|/if|}
@IsNumber() {|#if field.constraints.min|} @Min({|field.constraints.min|})
{|/if|} {|#if field.constraints.max|} @Max({|field.constraints.max|}) {|/if|}
{|field.names.casing.camel|}: {|#if field.flags.is_nullable|}number |
null{|else|}number{|/if|}; {|else|} // Unknown field type:
{|field.names.casing.camel|} {|/if|} {|/each|} }
```

## Template Sections Explained

### Imports

```codepurify
import { IsString, IsEmail, IsOptional, IsNumber, Min, Max } from
'class-validator';
```

Imports required validation decorators.

### Class Declaration

```codepurify
export class Create{| entity.names.casing.pascal |}DTO {
```

Creates class with "Create" prefix and entity name.

### Field Iteration

```codepurify
{|#each entity.fields.arrays.all.items as field|}
```

Loops through all entity fields.

### Primary Key Handling

```codepurify
{|#if field.flags.is_primary|} // Primary key excluded from create DTO {|else|}
```

Skips primary keys in create operations.

### String Fields

```codepurify
{|#if field.flags.is_nullable|} @IsOptional() {|/if|} {|#if
field.flags.is_email|} @IsEmail() {|else|} @IsString() {|/if|}
{|field.names.casing.camel|}: {|#if field.flags.is_nullable|}string |
null{|else|}string{|/if|};
```

Adds appropriate validation for string fields.

## Input Context

Simplified `types/user.json`:

```json
{
  "entity": {
    "names": {
      "original": "user",
      "casing": {
        "camel": "user",
        "pascal": "User",
        "kebab": "user"
      }
    },
    "fields": {
      "arrays": {
        "all": {
          "items": [
            {
              "names": {
                "original": "id",
                "casing": {
                  "camel": "id"
                }
              },
              "flags": {
                "is_primary": true,
                "is_number": true,
                "is_string": false
              }
            },
            {
              "names": {
                "original": "email",
                "casing": {
                  "camel": "email"
                }
              },
              "flags": {
                "is_string": true,
                "is_email": true,
                "is_nullable": false
              }
            },
            {
              "names": {
                "original": "age",
                "casing": {
                  "camel": "age"
                }
              },
              "flags": {
                "is_number": true,
                "is_nullable": true,
                "constraints": {
                  "min": 0,
                  "max": 120
                }
              }
            }
          ]
        }
      }
    }
  }
}
```

## Generated Output

`output/create-user.dto.ts`:

```ts
import {
  IsString,
  IsEmail,
  IsOptional,
  IsNumber,
  Min,
  Max,
} from "class-validator";

export class CreateUserDTO {
  // Primary key excluded from create DTO

  @IsEmail()
  email: string;

  @IsOptional()
  @IsNumber()
  @Min(0)
  @Max(120)
  age: number | null;
}
```
