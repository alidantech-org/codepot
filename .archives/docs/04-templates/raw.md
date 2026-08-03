---
title: Raw Blocks
description: Escaping template delimiters in special cases
---

# Raw Blocks

Escape template delimiters when they conflict with target syntax.

## Raw Block Syntax

```codepot
{|{raw}|} Content that should not be parsed {|{/raw}|}
```

## Why Raw Blocks Are Needed

### Vue Templates

Vue uses `{| ... |}` syntax for interpolation:

```codepot
{|{raw}|}
<template>
  <div>{{message}}</div>
</template>
{|{/raw}|}
```

### codepot Inside Templates

When generating codepot templates:

```codepot
{|{raw}|}
<script type="text/x-codepot-template">
  <div>{{name}}</div>
</script>
{|{/raw}|}
```

### HTML Interpolation Conflicts

When generating templates that use similar delimiters:

```codepot
{|{raw}|}
<!-- This should not be parsed by codepot -->
<div class="{{active ? 'active' : ''}}">
  Content here
</div>
{|{/raw}|}
```

## Before Raw Block

❌ Incorrect - codepot tries to parse `{| active |}`:

```codepot
<div class="{| active ? 'active' : '' |}">
  {| content |}
</div>
```

## After Raw Block

✅ Correct - Content preserved as-is:

```codepot
{|{raw}|}
<div class="{{active ? 'active' : ''}}">
  {{content}}
</div>
{|{/raw}|}
```

## Real Example: Generating Vue Component

Template: `templates/user.component.vue.codepot`

```codepot
<template>
  {|{raw}|}
  <div class="user-card">
    <h2>{{user.name}}</h2>
    <p>{{user.email}}</p>
    <button @click="editUser">Edit</button>
  </div>
  {|{/raw}|}
</template>

<script setup lang="ts">
  import { ref } from 'vue'; interface {| entity.names.casing.pascal |} {
  {|#each entity.fields.arrays.all.items as field|}
  {|field.names.casing.camel|}: {|#if field.flags.is_string}string{|/if|};
  {|/each|} } const {| entity.names.casing.camel |} = ref<{|
  entity.names.casing.pascal |}>({ {|#each entity.fields.arrays.all.items as
  field|} {|field.names.casing.camel|}: ''{|#unless @last|},{|/unless|}
  {|/each|} }); function editUser() { // Edit logic here }
</script>

<style scoped>
  {|{raw}|}
  .user-card {
    padding: 1rem;
    border: 1px solid #ccc;
    border-radius: 8px;
  }
  {|{/raw}|}
</style>
```

## Generated Output

`user.component.vue`:

```vue
<template>
  <div class="user-card">
    <h2>{{ user.name }}</h2>
    <p>{{ user.email }}</p>
    <button @click="editUser">Edit</button>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";

interface User {
  id: number;
  name: string;
  email: string;
}

const user = ref<User>({
  id: 0,
  name: "",
  email: "",
});

function editUser() {
  // Edit logic here
}
</script>

<style scoped>
.user-card {
  padding: 1rem;
  border: 1px solid #ccc;
  border-radius: 8px;
}
</style>
```

## Tips for Raw Blocks

- Use raw blocks only when necessary
- Keep raw blocks minimal
- Test generated output to ensure delimiters work correctly
- Consider using different delimiters if conflicts are frequent
