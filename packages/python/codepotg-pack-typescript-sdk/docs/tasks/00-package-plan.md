# TypeScript SDK pack tasks

## Package and manifest

- [ ] Add isolated package metadata, pack-provider entry point, package-data rules, and compatibility bounds.
- [ ] Add `CodepotgPack.yaml` with metadata, content discovery, ignore patterns, write policy, selections, files, bindings, language rules, dependencies, setup, and commands.
- [ ] Ensure every template target is inferred from its filename and no project-level language is required.

## Pack content

- [ ] Migrate representative model, enum, DTO, operation, client, error, configuration, documentation, and test templates.
- [ ] Replace system-owned barrels with authored `index.ts.jinja` templates receiving planned exports.
- [ ] Include unchanged static files such as `.gitignore`, `.env.example`, license, and sample configuration where appropriate.
- [ ] Add Gitignore-compatible pack exclusions and partial-template classification.
- [ ] Support modular, grouped, and monolithic generation profiles.

## Imports, bindings, and project integration

- [ ] Declare and document all public import, path, text, package-name, and artifact bindings.
- [ ] Support project aliases, relative imports, default barrels, binding groups, and external package imports.
- [ ] Declare typed Node runtime and development dependency contributions.
- [ ] Support npm, pnpm, and Yarn through project toolchain resolution rather than hardcoded commands.
- [ ] Add typed optional actions for dependency installation, ESLint fixes, formatting, and type checking under command policy.
- [ ] Provide `codepotg configure` questions, discovery hints, examples, and manual setup steps.

## Validation and migration

- [ ] Pass pack-manifest, template, static-file, binding, command, and output-planning contract suites.
- [ ] Generate small deterministic fixtures plus a realistic inspectable TypeScript SDK project.
- [ ] Compare migrated output with existing TypeScript packs and classify intentional differences.
- [ ] Prove the pack can be fetched from local and Git sources and locked by commit and digest.
- [ ] Version and publish independently.
