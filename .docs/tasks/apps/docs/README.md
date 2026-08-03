# Documentation application tasks

`apps/docs` is currently an active boundary with a local README, not yet a separate executable renderer.

Before implementation, plan the relationship between `apps/docs` and the documentation features currently inside `apps/site`. The accepted outcome must:

- preserve `.docs` as the only authored source;
- avoid duplicate renderers and build pipelines;
- preserve public URLs and redirects;
- define ownership of validation, search indexing, navigation compilation, and deployment;
- include migration and rollback evidence.

No implementation task is ready in this area until that ownership decision is approved.
