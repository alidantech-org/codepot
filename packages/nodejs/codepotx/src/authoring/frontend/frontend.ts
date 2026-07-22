import { normalizeInfo } from '../core/normalize';
import type { DefineFrontendOptions, FrontendBuilder, FrontendContext } from './frontend.types';
import type { JsonObject } from '@/contract/index';
export function defineFrontend(options: DefineFrontendOptions): FrontendBuilder {
  const info = options.info ? normalizeInfo(options.info) : undefined;
  const context: FrontendContext = {
    name: options.name,
    ...(options.platform ? { platform: options.platform } : {}),
    ...(options.framework ? { framework: options.framework } : {}),
    ...(options.metadata ? { metadata: options.metadata } : {}),
    ...(info ? { info } : {}),
  };
  const components: JsonObject[] = [...(options.components ?? [])];
  const screens: JsonObject[] = [...(options.screens ?? [])];
  const builder: FrontendBuilder = {
    context,
    components,
    screens,
    component(component: JsonObject): FrontendBuilder { components.push(component); return builder; },
    screen(screen: JsonObject): FrontendBuilder { screens.push(screen); return builder; },
  };
  return builder;
}
