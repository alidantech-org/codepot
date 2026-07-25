---
title: Resources and routes
description: Group contract meaning into resources and define typed HTTP operations, parameters, bodies, responses, caching, and sources.
product: codepot-openapi
package: codepot-openapi
order: 6
---

# Resources and routes

A resource groups the schemas, operations, persistence meaning, access rules, and frontend intent for one domain area.

## Define a resource

```ts
const orders = v1.defineResource({
  name: 'orders',
  route: '/orders',
  tags: ['Orders'],
});
```

- `name` is the stable Codepot resource identity.
- `route` is the resource-level HTTP prefix.
- tags and information notes provide OpenAPI and generator guidance.

## Define routes

```ts
orders.defineRoutes().routes((route) => ({
  listOrders: route
    .get('/')
    .query(schemas.OrderQuery)
    .response(schemas.Order.array()),

  getOrder: route
    .get('/:id')
    .response(schemas.Order),

  createOrder: route
    .post('/')
    .body(schemas.CreateOrder)
    .response(schemas.Order),

  updateOrder: route
    .patch('/:id')
    .body(schemas.UpdateOrder)
    .response(schemas.Order),

  deleteOrder: route
    .delete('/:id')
    .response(schemas.DeleteOrderResponse),
}));
```

The object key is the operation ID. Keep it stable because cache rules, frontend uses, generators, and clients may reference it.

## HTTP methods

The route factory supports the package's typed HTTP method model. `HttpMethod` is exported for consumers that need method values programmatically.

## Parameters

Routes can receive:

- path parameters;
- query parameters;
- header parameters;
- cookie parameters;
- reusable parameter component refs.

Declare route-level parameters once when all operations share them. Operation-specific declarations should remain on the operation.

A parameter keeps its name, location, required state, schema, style, explode behavior, examples, and source metadata.

## Request bodies

`.body(...)` accepts an inline schema use or a request-body component reference. Content types use version defaults unless an operation explicitly changes them.

## Responses

`.response(...)` defines the primary success response. Reusable response components and additional status responses can be registered when an operation has multiple meaningful outcomes.

Generators can inspect:

- success and error responses;
- primary response;
- schema refs by media type;
- response headers and links;
- operation role and target metadata.

## Route sources

Source definitions describe values that a frontend or generator can load for a field, selector, or relation.

A normalized source can include:

- source name;
- source operation;
- response field;
- item shape;
- key, label, and value fields.

Use sources to describe intent. Do not embed frontend fetch implementation inside the contract.

## Cache metadata

Route cache metadata can describe read policy and invalidation targets.

```ts
updateOrder.cache((cache) =>
  cache.invalidate.on('listOrders', 'getOrder'),
);
```

Invalidation operation IDs are resolved after the route registry is complete. Invalid targets are validation errors.

## Operation roles

`x-codegen` can classify operations as list, detail, create, update, delete, query, mutation, or action. Prefer explicit roles when naming alone is ambiguous.

## Route design guidance

- Keep operation IDs independent from framework handler names.
- Put shared route parameters at the resource route definition.
- Do not duplicate the resource prefix inside each operation path.
- Use request/response projections that communicate business meaning.
- Keep cache invalidation explicit and bounded.
- Add information notes for security, validation, observability, and implementation constraints that generators or AI tools must preserve.