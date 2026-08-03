---
title: Access, hooks, frontends, and information notes
description: Add target-neutral application behavior beyond ordinary OpenAPI operations.
product: codepot-openapi
package: codepot-openapi
order: 8
---

# Access, hooks, frontends, and information notes

OpenAPI describes HTTP shape well, but a generator often needs additional application meaning. `codepot-openapi` preserves that meaning through typed `x-codegen` metadata.

## Access policies

`defineAccess` creates named policies that can be reused by resources and operations.

An access policy can describe:

- public or authenticated access;
- roles and role sources;
- permissions;
- ownership rules;
- policy context and tags;
- implementation and security notes.

An operation references a policy instead of embedding framework guards or middleware.

```text
contract access policy
        ↓
resolved x-codegen access metadata
        ↓
NestJS guard / Express middleware / frontend permission check
```

Templates decide how to implement the policy for their target.

## Runtime hooks

`defineHooks` registers named lifecycle hooks. A route can attach hooks to phases such as:

- before handler;
- after success;
- after error.

Runtime metadata can also describe transport concerns:

- inbound IP, user agent, headers, and cookies;
- outbound cookies and headers.

Hooks identify required behavior. They do not contain executable project code.

## Frontend definitions

`defineFrontend` describes one explicitly authored frontend, for example `admin`, `customer`, or `mobile`.

A frontend can own:

- route prefix and folders;
- screens;
- reusable components;
- operation uses;
- schema uses;
- tags and information notes.

### Screens

A screen can describe:

- route and full route;
- path and query parameters;
- required components;
- operations used by the page;
- title, description, tags, and notes.

### Components

A component can describe:

- props;
- schemas;
- operations;
- tags;
- title, description, and implementation notes.

Codepot does not invent screens from CRUD operations when explicit frontend metadata is required. A generator should render only the selected or declared frontend contract.

## UI metadata

Resources and operations can expose UI intent such as:

- enabled or disabled;
- infer or explicit mode;
- role;
- effective inherited value;
- inference source and reason.

Authored and inferred values remain distinguishable so tools can explain why a screen or action exists.

## Information notes

`createInfoBuilder` and `normalizeInfo` support ordered notes for:

- explanation;
- access;
- implementation;
- validation;
- security;
- observability;
- UX;
- performance;
- testing;
- additional project-specific guidance.

Information notes are useful for developers and AI agents because they preserve why a contract decision exists, not only its machine shape.

## Design guidance

- Use access policies for semantic authorization, not framework class names.
- Use hooks for required lifecycle behavior, not arbitrary code strings.
- Define only frontends that the contract intentionally supports.
- Keep screen routes and operation IDs stable.
- Put detailed project implementation in template packs; keep the contract portable.
- Add information notes when a generator could otherwise produce technically valid but operationally wrong code.