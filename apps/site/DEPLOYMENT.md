# Codepot site deployment

The site is deployed as a Next.js standalone server built from the monorepo root.

The root build context is required because the site build reads public Markdown from `docs/` before `next build` runs.

## Files

```text
compose.yaml
.env.docker.example
apps/site/Dockerfile
apps/site/src/app/health/route.ts
```

## Published application mapping

The production domain is:

```text
https://code.alidantech.org
```

The reverse proxy forwards that domain to:

```text
http://localhost:3020
```

Docker Compose publishes host port `3020` to the application's internal container port `3000`:

```text
127.0.0.1:3020 -> container:3000
```

## Configure

Create a local Compose environment file:

```bash
cp .env.docker.example .env
```

Production values:

```dotenv
NEXT_PUBLIC_SITE_URL=https://code.alidantech.org
SITE_PORT=3020
SITE_BIND_ADDRESS=127.0.0.1
CODEPOT_SITE_IMAGE=codepot-site:latest
```

`NEXT_PUBLIC_SITE_URL` is passed as both a Docker build argument and a runtime environment variable. Rebuild the image when this value changes because Next.js public values and generated metadata can be embedded during the production build.

## Validate the Compose configuration

```bash
docker compose config
```

Confirm the rendered port mapping is:

```text
127.0.0.1:3020:3000
```

## Build and start

```bash
docker compose build --pull site
docker compose up -d site
```

## Check health

From the Docker host:

```bash
docker compose ps
curl --fail http://127.0.0.1:3020/health
```

Expected response:

```json
{"status":"ok","service":"codepot-site"}
```

## View logs

```bash
docker compose logs -f --tail=200 site
```

## Deploy an update

```bash
git pull --ff-only origin chatgpt/develop
docker compose build --pull site
docker compose up -d --remove-orphans site
```

## Stop

```bash
docker compose down
```

## Reverse proxy

The TLS-terminating reverse proxy for `code.alidantech.org` should forward requests to:

```text
http://127.0.0.1:3020
```

The container itself still listens on port `3000`; only the host-published port is `3020`.

## Image contents

The builder stage copies the monorepo so pnpm workspace resolution and root documentation synchronization work correctly. `.dockerignore` excludes dependency folders, build output, archives, the old CodepotX package, and the Python package.

The final runtime image copies only:

```text
.next/standalone
.next/static
public
```

The application runs as the non-root `nextjs` user. The Compose service drops Linux capabilities and enables `no-new-privileges`.

## Important checks

Before publishing the image, verify:

```bash
pnpm install --frozen-lockfile
pnpm --filter @codepot/site validate:docs
pnpm --filter @codepot/site typecheck
pnpm --filter @codepot/site build
docker compose config
docker compose build site
docker compose up -d site
curl --fail http://127.0.0.1:3020/health
```
