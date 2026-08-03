# Phase 11 — Shipping validation

Status: [ ]
Issue: open after site/docs deployment work
Depends on: Phases 08-10
Commits: pending
Validation: pending

## Goal

Prove the monorepo is publishable and deployable as a complete Codepot release candidate.

## Tasks

- [ ] Install the pinned workspace dependencies and update the lockfile.
- [ ] Run strict typechecks, tests, builds, package lint, Publint, and Are The Types Wrong for every publishable package.
- [ ] Run authoring → templating → generation through programmatic runtime and external CLI fixtures.
- [ ] Validate variable catalogs, template references, partials, dependencies, imports, manifests, rollback, and incremental no-change runs.
- [ ] Pack `codepotx` and `codepotx-cli` and install them into temporary consumer projects.
- [ ] Verify root and subpath exports, ESM behavior, consumer aliases, Windows paths, package sources, Git sources, and artifact sources.
- [ ] Verify no internal aliases, source-only files, caches, secrets, or peer Zod requirements leak into packages.
- [ ] Build and smoke-test `apps/site` in standalone Docker mode.
- [ ] Audit all issues, task files, documentation, migration notes, release notes, package metadata, and PR description.
- [ ] Close every completed issue and leave only evidence-backed limitations open.

## Rules

- Do not mark release checks complete without command output or repository evidence.
- Environment limitations must be exact and accompanied by local commands.
- No GitHub Actions workflow is permitted.
- The release candidate must be reproducible from a clean checkout.
