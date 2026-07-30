# Dart adapter task tracking

Read the package design, central language-adapter contract, path-expression specification, and agent rules before claiming work.

- Claim DART task IDs in `PARALLEL_WORK.md`.
- Core owns semantic name projections and path composition.
- This adapter validates Dart target filenames and renders Dart imports/exports; it does not select package folders or add filename conveniences to IR.
- Record exact tests and progress evidence.

Task files:

- [`00-package-plan.md`](00-package-plan.md)
- [`01-path-contract.md`](01-path-contract.md)
