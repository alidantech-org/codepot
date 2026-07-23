import type {
  TemplatingLoadRequest,
  TemplatingLoadResult,
} from '@/contract/index';
import type { TemplatingDependencies } from '../templating.types';
import { compileTemplatePack } from './compile-template-pack';

export async function loadTemplatePack(
  dependencies: TemplatingDependencies,
  request: TemplatingLoadRequest,
): Promise<TemplatingLoadResult> {
  return compileTemplatePack(dependencies, request);
}
