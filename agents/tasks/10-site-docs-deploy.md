# Phase 10 — Site, documentation, and deployment

Status: [~]
Issue: #12 open
Depends on: finished public contracts and CLI
Commits: site restart range `028611a5afc84218199778866a8ac047edf5b9df` through `fc7c1801034befc3ad2edb18f3f0524e2cdbfc59`
Validation: GitHub source reads compared the active site with the archived layout, landing, docs, theme, data, code-block, navigation, and asset files. A commit comparison from the pre-site head confirmed the active `apps/site` tree contains the archived component hierarchy and no temporary replacement components. Installed typecheck and Next production build remain pending because npm/GitHub DNS is unavailable and the root lockfile cannot be regenerated in this environment.

## Goal

Move the archived Next.js site into `apps/site`, preserve its exact visual design and component structure, tailor only its consumer-facing content to Codepot, render root Markdown documentation through `/docs` and `/docs/[slug]`, and provide production deployment paths without GitHub Actions.

## Tasks

- [x] Reuse the archived root layout, global theme, logo, navigation, mobile drawer, footer, background grid, glow decorations, fonts, and responsive behavior.
- [x] Reuse the archived landing component hierarchy: hero, features, interactive pipeline, examples, use cases, and CTA banner.
- [x] Rewrite landing content only for Codepot's three layers, AI-assisted coding benefits, and the in-progress Codepot Lang direction.
- [x] Remove the temporary replacement header, docs shell, and Markdown renderer created before the archived-design restart.
- [x] Reuse the archived docs index, grouped sidebar, mobile docs bar, right-side live table of contents, Markdown typography, copyable code blocks, and pager.
- [x] Limit public documentation pages to `/docs` and `/docs/[slug]` with Markdown files as the maintained content source.
- [x] Allowlist public docs through `docs/navigation.json`; maintainer-only deployment and release notes are not embedded into public routes.
- [x] Add functional documentation search while preserving the archived search-overlay design.
- [x] Add consumer-facing authoring, templating, generation, CLI, migration, safety, programmatic-use, and Codepot Lang documentation.
- [x] Add documentation validation for missing files, duplicate slugs, invalid slugs, frontmatter, and unpublished internal links.
- [x] Align `apps/site` with pnpm/Turbo and add root site development/build commands.
- [x] Configure Next.js standalone output, Docker deployment, non-root execution, `/health`, robots, sitemap, environment documentation, and optional Vercel configuration.
- [x] Preserve the account restriction against GitHub Actions; no workflow files were added.
- [ ] Regenerate and commit the workspace lockfile with the `apps/site` importer from a networked checkout.
- [ ] Run installed site typecheck, Next production build, Docker build, and route smoke checks.

## Rules

- The archived site is the visual and component baseline; active site work must not replace it with a new design.
- Landing content remains consumer-facing and explains how Codepot works rather than package internals.
- Root `docs/` is the authoritative Markdown source.
- Only navigation-listed consumer guides are embedded into the public application.
- The visible docs application uses only `/docs` and `/docs/[slug]` content routes.
- Deployment remains provider-neutral; Docker is the portable baseline.
- No `.github/workflows` files may be created.
