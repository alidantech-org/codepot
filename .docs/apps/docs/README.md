# Documentation application

`apps/docs` is an active application boundary reserved for a dedicated documentation experience. Canonical Markdown lives in `.docs`, and public content lives in `.docs/public`.

At present, `apps/site` still owns the working documentation renderer and build scripts. Moving that capability into `apps/docs` is future task-backed work; do not duplicate the renderer or create a second Markdown source.
