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

## Configure

Create a local Compose environment file:

```bash
cp .env.docker.example .env
```

Set the real public URL before building:

```dotenv
NEXT_PUBLIC_SITE_URL=https://codepot.dev
SITE_PORT=3000
SITE_BIND_ADDRESS=0.0.0.0
CODEPOT_SITE_IMAGE=codepot-site:latest
```

`NEXT_PUBLIC_SITE_URL` is passed as both a Docker build argument and a runtime environment variable. Rebuild the image when this value changes because Next.js public values and generated metadata can be embedded during the production build.

## Validate the Compose configuration

```bash
docker compose config
```

## Build and start

```bash
docker compose build --pull site
docker compose up -d site
```

## Check health

```bash
docker compose ps
curl --fail http://127.0.0.1:3000/health
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

For a public deployment, place Caddy, Nginx, an AWS load balancer, or another TLS-terminating reverse proxy in front of port `3000`.

When the reverse proxy runs on the same machine, bind the service to localhost:

```dotenv
SITE_BIND_ADDRESS=127.0.0.1
```

The proxy should forward requests to:

```text
http://127.0.0.1:3000
```

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
docker compose build site
docker compose up -d site
curl --fail http://127.0.0.1:3000/health
```
