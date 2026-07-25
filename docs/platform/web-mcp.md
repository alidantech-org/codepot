---
title: Codepot Web and MCP
description: Planned frontends that will reuse Codepot runtime operations, semantic artifacts, diagnostics, and generation capabilities.
order: 25
---

# Codepot Web and MCP

Codepot Web and Codepot MCP are planned frontends in the final platform.

They are included in the ecosystem configuration now so the site, footer, package model, and future documentation have stable places for links and status. They must not be presented as released products before implementations and distribution channels exist.

## Codepot Web

The web frontend is intended to provide browser-based workflows such as:

- project and contract exploration;
- semantic model visualization;
- diagnostics and workspace health;
- template-variable inspection;
- generation-plan review;
- safe execution and reports;
- package and integration discovery.

The web application should consume runtime operations and stable artifacts. It should not create an independent compiler or generator implementation.

## Codepot MCP

The MCP integration is intended to expose structured Codepot capabilities to AI agents, including:

- project and module context;
- contracts and semantic IR;
- diagnostics;
- package and symbol lookup;
- template variables;
- generation plans;
- controlled generation operations;
- documentation and architecture context.

This gives AI tools explicit project meaning instead of forcing them to repeatedly infer architecture from generated source files.

## Planned architecture

```text
Codepot Web       Codepot MCP       other clients
      \                |                /
        stable runtime operations and artifacts
                      ↓
       compiler, analysis, generation, diagnostics
```

## Link placeholders

GitHub repositories, hosted URLs, and package registries remain `null` with `tbd` status in `docs/ecosystem.json`. The site hides unavailable links instead of rendering broken buttons.
