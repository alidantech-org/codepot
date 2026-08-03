# Codepot site deployment

The site is deployed as a Next.js standalone server built from the monorepo root.

The root build context is required because the site consumes the workspace lockfile and canonical public documentation under `.docs/public` before `next build` runs.

## Production mapping

```text
https://code.alidantech.org
        ↓
http://127.0.0.1:3020
        ↓
container port 3000
```

## Environment

Create the local Compose environment file:

```bash
cp .env.docker.example .env
```

Expected production values:

```dotenv
NEXT_PUBLIC_SITE_URL=https://code.alidantech.org
SITE_PORT=3020
SITE_BIND_ADDRESS=127.0.0.1
CODEPOT_SITE_IMAGE=codepot-site:latest
```

Rebuild the image whenever `NEXT_PUBLIC_SITE_URL` changes because Next.js may embed public values during the build.

## Validate before deployment

```bash
corepack enable
pnpm install --frozen-lockfile
pnpm --filter @codepot/site validate:docs
pnpm --filter @codepot/site sync:docs
pnpm --filter @codepot/site typecheck
pnpm --filter @codepot/site build
docker compose config
```

## Build and start

```bash
docker compose build --pull site
docker compose up -d --force-recreate --remove-orphans site
```

For a fully clean recovery build:

```bash
docker compose down --remove-orphans
docker compose build --no-cache --pull site
docker compose up -d --force-recreate site
```

## Verify

```bash
docker compose ps
docker compose run --rm --entrypoint sh site -c 'test -f /app/apps/site/server.js'
curl --fail http://127.0.0.1:3020/health
curl --fail http://127.0.0.1:3020/docs
curl --fail http://127.0.0.1:3020/docs/dryv
```

Expected health response:

```json
{"status":"ok","service":"codepot-site"}
```

## Logs and stop

```bash
docker compose logs -f --tail=200 site
docker compose down
```

## Deploy repository updates

Work is delivered on `develop`:

```bash
git switch develop
git pull --ff-only origin develop
docker compose build --pull site
docker compose up -d --force-recreate --remove-orphans site
```

The final runtime image runs as the non-root `nextjs` user, drops Linux capabilities, enables `no-new-privileges`, and uses the standalone server prepared by the site's postbuild step.
