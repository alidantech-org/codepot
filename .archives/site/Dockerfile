# syntax=docker/dockerfile:1

FROM node:22-alpine AS deps
RUN apk add --no-cache curl
WORKDIR /app/site

COPY site/package.json site/package-lock.json* site/pnpm-lock.yaml* site/yarn.lock* ./

RUN npm ci

FROM node:22-alpine AS builder
WORKDIR /app/site

COPY --from=deps /app/site/node_modules ./node_modules
COPY site/ ./
COPY docs/ ../docs/

RUN npm run build

FROM node:22-alpine AS runner
WORKDIR /app/site

ENV NODE_ENV=production
ENV PORT=3000
ENV HOSTNAME=0.0.0.0

COPY --from=builder /app/site/package.json ./package.json
COPY --from=builder /app/site/node_modules ./node_modules
COPY --from=builder /app/site/.next ./.next
COPY --from=builder /app/site/public ./public
COPY --from=builder /app/site/next.config.* ./
COPY --from=builder /app/docs ../docs/

EXPOSE 3000

CMD ["npm", "start"]