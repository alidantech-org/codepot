// src/compiler/passes/09-meta.ts

import type { InfoDefinition } from '@/contract/types/ir/info/definition';
import type { UrlDefinition } from '@/contract/types/ir/url/definition';

import type { CompilerContext } from '../context/compiler-context';

// ============================================================================
// META NORMALIZATION
// ============================================================================

/**
 * Converts authoring info into IR info.
 *
 * At the moment the authoring info shape already matches the IR info shape.
 * Keep this function anyway so future normalization stays isolated here.
 */
function resolveInfo(input: CompilerContext['authoring']['info']): InfoDefinition {
  return {
    ...input,
  };
}

/**
 * Converts authoring URLs into IR URLs.
 *
 * URL normalization belongs here because URLs are root metadata, not compiler
 * graph nodes like entities, properties, or routes.
 */
function resolveUrls(input: CompilerContext['authoring']['urls']): UrlDefinition[] {
  return (input ?? []).map((url) => ({
    ...url,
    kind: url.kind as UrlDefinition['kind'],
    env: url.env as UrlDefinition['env'],
  }));
}

/**
 * Copies optional root metadata from authoring to IR.
 */
function resolveRootDefinitionItem(ctx: CompilerContext): void {
  const ir = ctx.ir as {
    description?: string;
    deprecated?: boolean;
    meta?: Record<string, unknown>;
  };

  if (ctx.authoring.description !== undefined) {
    ir.description = ctx.authoring.description;
  }

  if (ctx.authoring.deprecated !== undefined) {
    ir.deprecated = ctx.authoring.deprecated;
  }

  if (ctx.authoring.meta !== undefined) {
    ir.meta = ctx.authoring.meta;
  }
}

// ============================================================================
// PASS
// ============================================================================

/**
 * Compiles root contract metadata into the IR.
 *
 * This pass owns only:
 * - codepot version
 * - project key
 * - API version
 * - info
 * - urls
 * - root description/deprecated/meta
 *
 * It must not compile properties, schemas, resources, security, responses,
 * or content types.
 */
export function compileMeta(ctx: CompilerContext): void {
  ctx.ir.codepot = ctx.authoring.codepot;
  ctx.ir.key = ctx.authoring.key;
  ctx.ir.version = ctx.authoring.version;
  ctx.ir.info = resolveInfo(ctx.authoring.info);
  ctx.ir.urls = resolveUrls(ctx.authoring.urls);

  resolveRootDefinitionItem(ctx);
}
