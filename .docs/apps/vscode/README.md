# VS Code

Code target: planned `apps/vscode`

Status: planned Dryv Project Client frontend. Implementation begins at [`tasks/00-dryv-project-client-integration.md`](tasks/00-dryv-project-client-integration.md) after the shared TypeScript Dryv client is ready.

The VS Code app is a frontend/project client, not a second generator. It discovers local Dryv project resources, connects to local or remote `dryv-api`, shows build progress/diagnostics/artifacts, previews changes, and safely applies Dryv WriteInstructions through the shared Node project-client utilities.

It does not own Canonical IR meaning, pack selection, template context, caching, scheduling or rendering.

See the canonical Dryv architecture under `.docs/packages/python/dryv/`.
