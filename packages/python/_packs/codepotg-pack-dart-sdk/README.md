# codepotg-pack-dart-sdk

Installable modular Dart SDK template pack for CodepotG v2.

This package generates one standalone Dart SDK package from the closed semantic kernel. It owns its manifest, Dart/YAML/Markdown templates, macros, partials, static package files, authored export barrels, binding documentation, exact optional commands, and package documentation.

The templates author every Dart character, including types, nullability, literals, imports, exports, comments, annotations, serialization, and client logic. `codepotg-language-dart` supplies target detection, validation, and URI/path facts only.

This package represents one coherent standalone SDK product. Existing-project contribution, Flutter integration, or a materially different monolithic product should be separate packs rather than hidden profile/file-selection machinery.

See [`docs/design/README.md`](docs/design/README.md) and [`docs/tasks/00-package-plan.md`](docs/tasks/00-package-plan.md).
