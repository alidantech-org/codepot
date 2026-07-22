import type {
  TemplateContextValidateRequest,
  TemplateContextValidateResult,
  TemplateVariablesRequest,
  TemplateVariablesResult,
} from './requests.types';

/** Optional inspection surface implemented by templating and exposed by runtime. */
export interface TemplateIntrospectionPort {
  variables(request: TemplateVariablesRequest): Promise<TemplateVariablesResult>;
  validateContext(request: TemplateContextValidateRequest): Promise<TemplateContextValidateResult>;
}
