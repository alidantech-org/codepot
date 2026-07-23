import type {
  TemplateContextRequest,
  TemplateContextResult,
  TemplateContextValidateRequest,
  TemplateContextValidateResult,
  TemplateRenderRequest,
  TemplateRenderResult,
  TemplateVariablesRequest,
  TemplateVariablesResult,
  TemplatingCompileRequest,
  TemplatingCompileResult,
  TemplatingLoadRequest,
  TemplatingLoadResult,
  TemplatingValidateRequest,
  TemplatingValidateResult,
} from '@/contract/index';
import { compileTemplatePack } from './application/compile-template-pack';
import { loadTemplatePack } from './application/load-template-pack';
import { validateTemplatePack } from './application/validate-template-pack';
import { createCompiledTemplateContext } from './context/create-template-context';
import { renderTemplateFiles } from './rendering/render-template-files';
import type {
  TemplatingDependencies,
  TemplatingEngine,
} from './templating.types';
import { listTemplateVariables } from './variables/list-template-variables';
import { validateCompiledTemplateContext } from './variables/validate-template-context';

/** Default autonomous implementation of the public templating contracts. */
export class DefaultTemplatingEngine implements TemplatingEngine {
  readonly #dependencies: TemplatingDependencies;

  constructor(dependencies: TemplatingDependencies) {
    this.#dependencies = dependencies;
  }

  load(request: TemplatingLoadRequest): Promise<TemplatingLoadResult> {
    return loadTemplatePack(this.#dependencies, request);
  }

  validate(request: TemplatingValidateRequest): Promise<TemplatingValidateResult> {
    return validateTemplatePack(this.#dependencies, request);
  }

  compile(request: TemplatingCompileRequest): Promise<TemplatingCompileResult> {
    return compileTemplatePack(this.#dependencies, request);
  }

  createContext(request: TemplateContextRequest): Promise<TemplateContextResult> {
    return createCompiledTemplateContext(request);
  }

  variables(request: TemplateVariablesRequest): Promise<TemplateVariablesResult> {
    return listTemplateVariables(this.#dependencies, request);
  }

  validateContext(
    request: TemplateContextValidateRequest,
  ): Promise<TemplateContextValidateResult> {
    return validateCompiledTemplateContext(this.#dependencies, request);
  }

  render(request: TemplateRenderRequest): Promise<TemplateRenderResult> {
    return renderTemplateFiles(this.#dependencies, request);
  }
}

export function createTemplatingEngine(
  dependencies: TemplatingDependencies,
): TemplatingEngine {
  return new DefaultTemplatingEngine(dependencies);
}
