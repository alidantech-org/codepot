---
title: Glossary
description: Shared terminology used across the Codepot prototypes, JavaScript runtime, and Rust platform.
order: 53
---

# Glossary

## Authoring

The user-facing process of describing typed software intent before generation.

## CodepotG

The supported Python and Jinja generator package, published as `codepotg`.

## Codepot Lang

The strongly typed Rust language at the center of the final platform.

## Consumer task

A project-owned generation task that selects semantic input, templates, output, variables, commands, and cleanup policy.

## Contract

A reusable description of software facts such as schemas, resources, operations, relationships, access, and lifecycle rules.

## Frontend

A user or tool interface over a shared runtime: CLI, editor, web app, MCP server, desktop tool, or embedded API.

## IR

Intermediate representation. In Codepot Lang, target-neutral semantic output produced after strong analysis.

## Managed file

A generated file whose ownership and digest are tracked so it can be updated or safely cleaned later.

## Immutable file

A generated scaffold that may be created when absent but is preserved on later runs.

## Manifest

A record of generated file ownership, digests, and task state used for changed-aware writes and guarded cleanup.

## Normalized generation context

The generator-facing model derived from source contracts before templates are rendered.

## OpenAPI

The standard API document used as the interchange boundary between `codepot-openapi` and `codepotg`.

## Runtime operation

A typed request/result pair exposed by `codepotx` or the final platform for use by multiple frontends.

## Template pack

Reusable implementation patterns, paths, partials, helpers or filters, and lifecycle policy for producing target files.

## `x-codegen`

Optional Codepot metadata embedded in OpenAPI for richer resource, entity, access, frontend, runtime, and generator behavior.
