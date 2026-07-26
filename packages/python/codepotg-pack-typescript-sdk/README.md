# codepotg-pack-typescript-sdk

Installable modular TypeScript SDK template pack for CodepotG v2.

The pack consumes the closed kernel through group-rooted schema and operation contexts. Its templates, macros, partials, and static files author every TypeScript character, including types, imports, exports, literals, comments, errors, and client methods.

The pack is heterogeneous and self-describing: TypeScript templates, authored barrels, JSON/Markdown/package templates, unchanged static files, public bindings, exact optional commands, and documentation live behind one `CodepotgPack.yaml` contract.

This package represents one coherent modular SDK product. A materially different monolithic, framework-specific, or host-contribution product should be a separate pack rather than hidden manifest profile/file-selection machinery.

`codepotg-language-typescript` supplies target detection, validation, and module-path facts only. It does not generate TypeScript syntax.

See [`docs/design/README.md`](docs/design/README.md) and [`docs/tasks/00-package-plan.md`](docs/tasks/00-package-plan.md).
