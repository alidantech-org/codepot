# Site tasks

`apps/site` is active and currently owns both the marketing website and the working documentation renderer.

Site tasks must preserve:

- `.docs/public` as the canonical public source;
- generated files under `apps/site/src/generated` as generated-only;
- documentation validation before build;
- stable `/docs` URLs and redirects;
- separation between site UI code and authored Markdown.

The future extraction of documentation rendering into `apps/docs` requires a separate approved architecture and migration task.
