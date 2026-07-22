# Phase 10 — Site, documentation, and deployment

Status: [ ]
Issue: open after generation hardening
Depends on: finished public contracts and CLI
Commits: pending
Validation: pending

## Goal

Move the archived Next.js site into `apps/site`, tailor it to the new Codepot architecture, make root `docs/` the documentation source of truth, and provide production deployment paths without GitHub Actions.

## Tasks

- [ ] Copy `archives/site` into `apps/site` while preserving its visual design and useful components.
- [ ] Align the app with the pnpm/Turbo TypeScript monorepo and shared root compiler settings.
- [ ] Remove Codepurify and outdated OpenAPI-first wording.
- [ ] Add Codepot authoring, templating, generation, runtime, CLI, migration, and template-variable documentation.
- [ ] Make the site read root `docs/` content and generated template-variable catalog data.
- [ ] Add generated API/reference pages from package exports and stable contracts where practical.
- [ ] Add search, navigation, code examples, version metadata, edit links, sitemap, robots, and metadata.
- [ ] Add package scripts that validate documentation links, examples, and catalog freshness.
- [ ] Configure Next.js standalone output for container deployment.
- [ ] Add a multi-stage Dockerfile, health endpoint, deployment README, and provider-neutral environment documentation.
- [ ] Add optional Vercel project configuration without adding GitHub Actions.
- [ ] Add site build, typecheck, lint, and route/content tests.

## Rules

- Root `docs/` is the authoritative documentation content.
- Documentation examples are compiled or validated by repository checks.
- The site may import only public package APIs and generated documentation data.
- Deployment remains provider-neutral; Docker is the portable baseline.
- No `.github/workflows` files may be created.
