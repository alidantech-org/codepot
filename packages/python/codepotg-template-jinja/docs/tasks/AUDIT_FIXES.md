# Audit fix handoff — `codepotg-template-jinja`

Use this file as the scoped handoff and completion record for the PR #28 audit repairs.

## Branches

```text
Base: chatgpt/codepotx-restart
Audit fix branch: chatgpt/codepotx-restart-jinja-audit-fixes
Release gate branch: chatgpt/codepotx-restart-jinja-release-gates
```

Only one slash was used. No `.github/**` file was created or modified.

## Required reading

```text
packages/python/codepotg-template-jinja/docs/audits/2026-07-27-pr-28-audit.md
packages/python/codepotg-template-jinja/docs/ENGINE_CONTRACT.md
packages/python/codepotg-template-jinja/docs/tasks/00-package-plan.md
packages/python/codepotg-template-jinja/docs/tasks/PROGRESS.md
packages/python/codepotg-v2/docs/00-governance/00-approved-architecture.md
packages/python/codepotg-v2/docs/04-plugins/03-template-engine-adapter-contract.md
```

## Completed work

1. Ran the complete core and Jinja release commands against package trees reconstructed from the current base through GitHub's authenticated contents API and checked against current branch blob identities.
2. Ran Ruff check and format check with the official Ruff 0.16.0 Linux release artifact.
3. Built the real core and Jinja wheel/sdist artifacts with PyPA Build 1.5.0 and the declared setuptools backend.
4. Installed both real wheels into a fresh environment and repeated entry-point, simple-render, static-partial, and denied-loop-callable checks.
5. Recorded exact evidence in `docs/tasks/PROGRESS.md`.
6. Kept JINJA-008 blocked; no named-output contract was invented.
7. Kept `loop.cycle()` and `loop.changed()` deliberately denied and covered both by exact compatibility tests.
8. Corrected root non-string source diagnostics to `JINJA_TEMPLATE_INVALID` while preserving `JINJA_PARTIAL_INVALID` for partials.
9. Added no filesystem loader, pack-provider access, target rendering, writing, commands, private core imports, or GitHub automation.

## Release verification

- [x] Ruff check passed for core `src tests`.
- [x] Ruff format check passed for all 59 core files.
- [x] Ruff check passed for Jinja `src tests benchmarks`.
- [x] Ruff format check passed for all 65 Jinja files.
- [x] Complete real-core package suite passed: 30 tests.
- [x] Complete Jinja suite passed against that core: 153 tests.
- [x] Core wheel and sdist built.
- [x] Jinja wheel and sdist built.
- [x] Fresh wheel-only environment discovered `codepotg.template_engines/jinja`.
- [x] Fresh wheel-only simple rendering produced `Hello World`.
- [x] Fresh wheel-only static-partial rendering produced `ABC`.
- [x] Fresh wheel-only `loop.cycle()` remained denied with `JINJA_CALLABLE_DENIED`.
- [x] GitHub branch comparison is scoped to committed Jinja package files; no `.github/**` or core implementation file changed.

The environment could not perform a conventional network clone because direct DNS remained unavailable. Verification therefore used exact current-branch package files retrieved through the authenticated GitHub connector, with source identities checked against GitHub blob SHAs. The release branch itself contains only committed changes, so there is no uncommitted remote state to report.

## Files allowed

```text
packages/python/codepotg-template-jinja/**
packages/python/codepotg-v2/docs/tasks/PARALLEL_WORK.md
```

Core implementation files remain unchanged.

## Completion gate

The PR #28 audit repair and current-port release gate are complete:

- all existing and added compatibility/diagnostic tests pass;
- Ruff and formatting pass;
- the real core suite passes;
- wheel/sdist builds pass;
- real-wheel isolated discovery/rendering passes;
- the scoped branch diff is fully committed and reviewed;
- task/progress status contains exact evidence.

JINJA-008 named outputs, pack-registry integration, target-compatible partial metadata, project/pack rule decoding, and runtime cache-port integration remain blocked until their public contracts exist. They are future integration lanes, not incomplete work in this release.
