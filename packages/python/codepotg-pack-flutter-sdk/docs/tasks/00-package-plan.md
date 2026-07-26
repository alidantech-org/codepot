# Flutter SDK pack tasks

## Package and manifest

- [ ] Add isolated package metadata, pack-provider entry point, package-data rules, and compatibility bounds.
- [ ] Add `CodepotgPack.yaml` with Flutter framework requirements, Dart language rules, content discovery, bindings, Pub dependencies, setup, commands, and lifecycle policy.
- [ ] Declare supported integration traits: standalone package, owned folder, and contributed files.

## Pack content

- [ ] Migrate Flutter API service, models, serialization, providers or adapters, errors, exports, examples, and documentation templates without moving Dart syntax into the framework pack.
- [ ] Use authored export templates and include static analysis, ignore, environment-example, asset, and package files where useful.
- [ ] Support modular and monolithic profiles plus folder-pattern fan-out.
- [ ] Keep application-specific UI and state-management assumptions behind explicit profiles or options.

## Bindings, dependencies, and setup

- [ ] Declare and document bindings for HTTP client, authentication token source, error mapping, logging, base URLs, and project-owned abstractions.
- [ ] Support a project barrel or package import for groups of bindings.
- [ ] Declare typed Flutter and Dart hosted, Git, path, runtime, and development dependencies.
- [ ] Detect existing Flutter projects, package names, `pubspec.yaml`, workspace paths, and compatible SDK versions.
- [ ] Add approved typed actions for `flutter pub get`, formatting, analysis, tests, and build runners.
- [ ] Provide configure questions, discovery candidates, placeholders, and manual integration reports.

## Validation and migration

- [ ] Pass manifest, framework capability, template, static-file, binding, dependency, and command contract suites.
- [ ] Generate a realistic inspectable Flutter package and an existing-application integration fixture.
- [ ] Compare with existing Flutter pack behavior and classify differences.
- [ ] Prove Git-hosted public and private pack resolution and digest-bound command approval.
- [ ] Version and publish independently.
