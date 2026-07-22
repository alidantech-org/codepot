import type {
  CompiledTemplatePack,
  GenerationPlan,
  RenderedGeneration,
} from '@/contract/index';

import type { GenerationDependencies } from './generation.types';

export async function readRenderedGenerationCache(
  plan: GenerationPlan,
  templates: CompiledTemplatePack,
  dependencies: Pick<GenerationDependencies, 'cache' | 'data'>,
): Promise<RenderedGeneration | null> {
  const entry = await dependencies.cache.get(renderCacheKey(plan, templates));
  if (!entry || entry.value.encoding !== 'utf8') return null;
  const rendered = dependencies.data.parseJson<RenderedGeneration>(entry.value.data);
  if (
    rendered.header?.kind !== 'codepot.rendered-generation'
    || rendered.header.sourceDigest !== plan.header.contentDigest
  ) return null;
  return rendered;
}

export async function writeRenderedGenerationCache(
  plan: GenerationPlan,
  templates: CompiledTemplatePack,
  rendered: RenderedGeneration,
  dependencies: Pick<GenerationDependencies, 'cache' | 'data' | 'clock'>,
): Promise<void> {
  await dependencies.cache.set({
    key: renderCacheKey(plan, templates),
    value: { encoding: 'utf8', data: dependencies.data.stringifyJson(rendered) },
    digest: rendered.header.contentDigest,
    createdAt: dependencies.clock.now(),
  });
}

export function renderCacheKey(plan: GenerationPlan, templates: CompiledTemplatePack): string {
  return `generation:render:${plan.header.contentDigest}:${templates.header.contentDigest}`;
}
