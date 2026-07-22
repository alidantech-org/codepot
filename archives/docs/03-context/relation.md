---
title: Relation Context
description: Working with entity relations in templates
---

# Relation Context

Relation context provides data about entity relationships.

## Relation Structure

```codepurify
{| relation.module.* |} // Module import info {| relation.property.* |} //
Property name on entity {| relation.type.* |} // Relation type details
```

## Module Information

```codepurify
{| relation.module.path |} // "./profile.entity" {| relation.module.name |} //
"Profile" {| relation.module.import_name |} // "Profile"
```

## Property Information

```codepurify
{| relation.property.name |} // "profile" {| relation.property.casing.camel |}
// "profile" {| relation.property.casing.pascal |} // "Profile"
```

## Type Information

```codepurify
{| relation.type.kind |} // "one-to-one", "one-to-many" {| relation.type.target
|} // "profile" {| relation.type.target_entity |} // "Profile"
```

## Import Example

```codepurify
{|#each entity.relations.arrays.all.items as relation|} import {
{|relation.module.import_name|} } from '{|relation.module.path|}'; {|/each|}
```

## Type Definition Example

```codepurify
export class {| entity.names.casing.pascal |} { {|#each
entity.relations.arrays.one_to_one.items as relation|} @OneToOne(() =>
{|relation.type.target_entity|}) @JoinColumn() {|relation.property.name|}:
{|relation.type.target_entity|}; {|/each|} {|#each
entity.relations.arrays.one_to_many.items as relation|} @OneToMany(() =>
{|relation.type.target_entity|},
'{|relation.type.target|}.{|relation.property.name|}')
{|relation.property.name|}: {|relation.type.target_entity|}[]; {|/each|} {|#each
entity.relations.arrays.many_to_one.items as relation|} @ManyToOne(() =>
{|relation.type.target_entity|}) {|relation.property.name|}:
{|relation.type.target_entity|}; {|/each|} }
```

## Real Template Snippet

```codepurify
// Imports {|#each entity.relations.arrays.all.items as relation|} import {
{|relation.names.casing.pascal|} } from './{|relation.module.path|}'; {|/each|}
// Class definition export class {| entity.names.casing.pascal |} { // Fields...
// Relations {|#each entity.relations.arrays.many_to_one.items as relation|}
@ManyToOne(() => {|relation.names.casing.pascal|}) {|relation.property.name|}:
{|relation.names.casing.pascal|}; {|/each|} }
```

## Relation Types

- **one-to-one** - Single related entity
- **one-to-many** - Array of related entities
- **many-to-one** - Single parent entity
- **many-to-many** - Array with join table

Relation context enables proper import statements and type definitions for entity relationships.
