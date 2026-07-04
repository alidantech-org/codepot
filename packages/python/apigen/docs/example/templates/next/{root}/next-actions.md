# Next Server Actions

This generator emits two kinds of server action helpers:

- Operation actions, such as `login`, `createUser`, or `updateUser`.
- Form actions, such as `loginAction`, `createUserAction`, or `updateUserAction`, generated when an operation is marked for UI form usage.

Operation actions accept typed input objects:

```ts
await login({
  body: {
    email: 'admin@example.com',
    password: 'secret',
  },
  options: {},
});
```

Form actions accept the `useActionState` shape:

```ts
const [state, action, pending] = useActionState(loginAction, null);

return (
  <form action={action}>
    <input name="email" />
    <input name="password" type="password" />
    <button disabled={pending}>Sign in</button>
  </form>
);
```

The form action returns:

```ts
{
  response,
  formdata
}
```

`response` is the API response. `formdata` is the cleaned request body that was sent.

## Reserved Fields

Generated form actions reserve fields that start with `__`. These fields are used by the action wrapper and are removed before the API payload is created.

Supported reserved fields:

```txt
__redirect_path
__delete
__delete:fieldName
__json_parse
__json_parse:fieldName
__boolean
__boolean:fieldName
__number
__number:fieldName
__date
__date:fieldName
__path:paramName
```

Use normal field names for API payload fields. Use `__...` fields only for action metadata.

## Redirects

To redirect after a successful response, include:

```tsx
<input type="hidden" name="__redirect_path" value="/dashboard" />
```

The action redirects only when:

```ts
response.success === true
```

If the response is not successful, the action returns `{ response, formdata }` without redirecting.

## Deleting Fields From Payload

If a form contains UI-only fields, mark them for deletion with `__delete`.

For example, if your API rejects this:

```json
{
  "success": false,
  "errors": [
    {
      "field": "redirectPath",
      "message": "property redirectPath should not exist"
    },
    {
      "field": "sessionData",
      "message": "property sessionData should not exist"
    }
  ]
}
```

Do not submit `redirectPath` as a body field. Use the reserved redirect field:

```tsx
<input type="hidden" name="__redirect_path" value="/dashboard" />
```

To remove `sessionData` from the API body:

```tsx
<input type="hidden" name="__delete" value="sessionData" />
```

Or:

```tsx
<input type="hidden" name="__delete:sessionData" value="1" />
```

Full example:

```tsx
<form action={loginAction}>
  <input name="email" />
  <input name="password" type="password" />

  <input type="hidden" name="__redirect_path" value="/dashboard" />
  <input type="hidden" name="__delete" value="sessionData" />

  <button>Sign in</button>
</form>
```

The resulting API body contains only:

```ts
{
  email,
  password
}
```

## Type Coercion

The generated action helpers use `getCleanFormData` from `next-api-bridge/form`.

To coerce fields, add reserved metadata fields:

```tsx
<input type="hidden" name="__boolean" value="emailVerified" />
<input type="hidden" name="__number" value="capacity" />
<input type="hidden" name="__date" value="startsAt" />
<input type="hidden" name="__json_parse" value="roles" />
```

Equivalent colon form:

```tsx
<input type="hidden" name="__boolean:emailVerified" value="1" />
<input type="hidden" name="__number:capacity" value="1" />
<input type="hidden" name="__date:startsAt" value="1" />
<input type="hidden" name="__json_parse:roles" value="1" />
```

## Arrays And Objects

The current `getCleanFormData` implementation is best used with JSON for arrays and nested objects.

For arrays:

```tsx
<input type="hidden" name="roles" value={JSON.stringify(['admin', 'user'])} />
<input type="hidden" name="__json_parse:roles" value="1" />
```

For nested objects:

```tsx
<input type="hidden" name="sessionData" value={JSON.stringify({ device: 'web' })} />
<input type="hidden" name="__json_parse:sessionData" value="1" />
```

If a nested object is only for UI state and should not be sent:

```tsx
<input type="hidden" name="sessionData" value={JSON.stringify({ device: 'web' })} />
<input type="hidden" name="__delete:sessionData" value="1" />
```

## Path Params

Generated UI form actions read path params from reserved fields:

```tsx
<input type="hidden" name="__path:userId" value={user.id} />
```

This avoids collisions with body fields named `userId`.

## Importing

Import server actions directly from their generated server action file:

```ts
import { loginAction } from '@/gen/server/actions/auth.actions';
```

Do not re-export action files from a client-facing barrel. A file with `'use server'` should only export async functions.

