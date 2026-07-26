# Flutter SDK/integration pack design reference

## Purpose

This pack applies Flutter framework conventions on top of the Dart language adapter and Dart ecosystem adapter. Flutter is not a language alias.

## Planned profiles

- `standalonePackage` — generated Flutter/Dart package with owned pubspec and package assets;
- `existingApp` — files and typed pubspec/assets contributions to a host Flutter app;
- `minimalClient` — models/client/errors only;
- `providerIntegration` — optional explicit provider/state integration;
- `monolithic` — aggregate API layer where useful.

## File examples

```text
templates/
├── lib/src/models/model.dart.jinja
├── lib/src/api/api_client.dart.jinja
├── lib/src/api/operation.dart.jinja
├── lib/src/errors/api_error.dart.jinja
├── lib/src/providers/api_provider.dart.jinja
├── lib/flutter_api.dart.jinja
├── pubspec.yaml.jinja
├── README.md.jinja
├── analysis_options.yaml
├── .env.example
└── assets/example.json
```

Dart exports are authored templates. Static files and assets copy by default. Provider/UI-specific files activate only through explicit profile/options.

## Project configuration example

```yaml
packs:
  mobileApi:
    use:
      github: alidantech-org/codepotg-flutter-sdk-pack
      ref: v2.0.0
    source: backendApi
    profile: existingApp
    output:
      root: apps/mobile/lib/generated_api
    bindings:
      transport:
        symbol: AppHttpClient
        from:
          package: riderescue_core
          path: network/app_http_client.dart
      authToken:
        symbol: TokenProvider
        from:
          barrel: "package:riderescue_core/auth.dart"
```

## Pack responsibilities

- Flutter-specific file layout and integration profiles;
- bindings for transport, auth, base URL, errors, logging, and optional provider layer;
- typed Flutter/Dart dependencies, assets, and pubspec intent;
- configure detection and manual setup;
- optional approved pub get, build runner, format, analyze, and test actions.

## Boundaries

Dart syntax belongs to the Dart adapter. Pubspec merging belongs to the ecosystem adapter. The pack does not hardcode one state-management library by default and does not parse old pack formats.

See `../tasks/00-package-plan.md`.
