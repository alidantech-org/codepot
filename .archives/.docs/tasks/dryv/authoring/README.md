# Author package tasks

- [`00-master-plan.md`](00-master-plan.md) contains the complete AUTHOR-001..AUTHOR-030 implementation ledger.
- [`01-dependencies-and-parallelism.md`](01-dependencies-and-parallelism.md) defines safe batches, ownership, synchronization, and merge order.
- [`PARALLEL_WORK.md`](PARALLEL_WORK.md) records package-local claims.
- [`PROGRESS.md`](PROGRESS.md) records immutable evidence and corrections.

A task is complete only with implementation, focused tests, architecture tests, typing checks where relevant, documentation, and exact command evidence.

Unsupported core concepts are blocked with the exact missing public contract. They are never considered implemented through extensions, tags, raw values, or package-private IR.
