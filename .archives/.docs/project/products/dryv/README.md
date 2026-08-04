# Dryv product family

Dryv is the active Codepot implementation family.

- [`runtime/`](runtime/README.md) — canonical runtime, IR, planning, generation, plugins, and managed output.
- [`authoring/`](authoring/README.md) — typed authoring and compilation into Runtime IR.
- [`cli/`](cli/README.md) — terminal frontend.
- [`template-jinja/`](template-jinja/README.md) — Jinja template-engine adapter.
- [`language-typescript/`](language-typescript/README.md) — TypeScript target facts and validation.
- [`language-dart/`](language-dart/README.md) — Dart target facts and validation.

All packages depend inward on the public runtime contracts. The runtime must not depend on frontends or optional adapters.
