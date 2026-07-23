import type {
  TemplateContextRequest,
  TemplateContextResult,
  TemplateRenderRequest,
  TemplateRenderResult,
  TemplatingCompileRequest,
  TemplatingCompileResult,
  TemplatingLoadRequest,
  TemplatingLoadResult,
  TemplatingValidateRequest,
  TemplatingValidateResult,
} from '../../operations/templating/index';

export interface TemplatingPort {
  load(request: TemplatingLoadRequest): Promise<TemplatingLoadResult>;
  validate(request: TemplatingValidateRequest): Promise<TemplatingValidateResult>;
  compile(request: TemplatingCompileRequest): Promise<TemplatingCompileResult>;
  createContext(request: TemplateContextRequest): Promise<TemplateContextResult>;
  render(request: TemplateRenderRequest): Promise<TemplateRenderResult>;
}
