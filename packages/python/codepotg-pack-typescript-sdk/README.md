# codepotg-pack-typescript-sdk

Installable default TypeScript SDK template pack for CodepotG v2.

This package will prove that a pack can be heterogeneous and self-describing: TypeScript templates, authored barrel templates, JSON or Markdown templates, unchanged static files, public bindings, Node dependency contributions, setup guidance, and optional finishing commands all live behind one `CodepotgPack.yaml` contract.

The pack must support both modular generation and a monolithic profile that can generate the complete SDK in one file. It relies on `codepotg-language-typescript` and a compatible template-engine adapter but must not receive special access to core.

See [`docs/tasks/00-package-plan.md`](docs/tasks/00-package-plan.md).
