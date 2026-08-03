---
title: Names & Casing System
description: String transformation and naming conventions
---

# Names & Casing System

The names system provides consistent string transformations across all templates.

## Input Example

```json
{
  "names": {
    "original": "userProfile"
  }
}
```

## Available Casings

### camel

```codepot
{| entity.names.casing.camel |} // Output: userProfile
```

### pascal

```codepot
{| entity.names.casing.pascal |} // Output: UserProfile
```

### snake

```codepot
{| entity.names.casing.snake |} // Output: user_profile
```

### kebab

```codepot
{| entity.names.casing.kebab |} // Output: user-profile
```

### constant

```codepot
{| entity.names.casing.constant |} // Output: USER_PROFILE
```

### title

```codepot
{| entity.names.casing.title |} // Output: User Profile
```

## Original Name

```codepot
{| entity.names.original |} // Output: userProfile
```

## Singular/Plural

```codepot
{| entity.names.singular.casing.pascal |} // Output: User {|
entity.names.plural.casing.pascal |} // Output: Users
```

## Real Template Usage

```codepot
// Class name export class {| entity.names.casing.pascal |} { {|#each
entity.fields.arrays.all.items as field|} // Property name
{|field.names.casing.camel|}: {|#if field.flags.is_string}string{|/if|};
{|/each|} } // File name const fileName = "{| entity.names.casing.kebab
|}.dto.ts"; // API endpoint const endpoint = "/api/{|
entity.names.plural.casing.kebab |}";
```

## Complex Input

```json
{
  "names": {
    "original": "orderManagementService"
  }
}
```

### Transformations

- camel → orderManagementService
- pascal → OrderManagementService
- snake → order_management_service
- kebab → order-management-service
- constant → ORDER_MANAGEMENT_SERVICE
