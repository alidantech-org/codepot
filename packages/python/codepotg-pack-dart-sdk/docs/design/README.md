# Dart SDK pack design reference

## Purpose

This pack generates a Dart API SDK either as a standalone package with an owned `pubspec.yaml` or as files contributed to an existing Dart package.

## Planned profiles

- `standalonePackage` — owns package folder, pubspec, analysis config, docs, examples, and generated library;
- `contribute` — generates into an existing package and declares pubspec contributions;
- `modular` — per-model/service output plus authored exports;
- `monolithic` — one aggregate Dart output where desired;
- `minimal` — selected core outputs.

## File examples

```text
templates/
├── lib/src/models/model.dart.jinja
├── lib/src/models/enum.dart.jinja
├── lib/src/client/operation.dart.jinja
├── lib/api_sdk.dart.jinja
├── lib/all.dart.jinja
├── pubspec.yaml.jinja
├── README.md.jinja
├── analysis_options.yaml
├── .gitignore
└── _partials/license.txt.jinja
```

Export files are authored templates. Static analysis and ignore files copy without rendering.

## Project configuration example

```yaml
packs:
  dartSdk:
    use:
      github: alidantech-org/codepotg-dart-sdk-pack
      ref: v2.0.0
    source: backendApi
    profile: standalonePackage
    output:
      root: packages/api_sdk
    options:
      packageName: defytickets_api
    bindings:
      authToken:
        symbol: TokenProvider
        from:
          package: shared_auth
          path: token_provider.dart
```

## Pack responsibilities

- SDK selections and profiles;
- Dart/YAML/Markdown templates and static assets;
- public bindings and package-name/import requirements;
- Dart and Jinja pack rules;
- typed pub dependency/manifest intent;
- configure questions and manual integration;
- optional pub get, format, analyze, test, and build-runner actions under approval policy.

## Boundaries

Dart syntax and URI rendering belong to `codepotg-language-dart`. Pubspec contribution logic belongs to the Dart ecosystem adapter. This pack does not parse old pack files or import old generator code.

See `../tasks/00-package-plan.md`.
