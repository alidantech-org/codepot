import type { JsonObject } from '@/contract/index';
import type { InfoInput, NormalizedInfo } from '../core/authoring.types';
export interface DefineFrontendOptions { readonly name: string; readonly platform?: string; readonly framework?: string; readonly components?: readonly JsonObject[]; readonly screens?: readonly JsonObject[]; readonly metadata?: JsonObject; readonly info?: InfoInput; }
export interface FrontendContext { readonly name: string; readonly platform?: string; readonly framework?: string; readonly metadata?: JsonObject; readonly info?: NormalizedInfo; }
export interface FrontendBuilder { readonly context: FrontendContext; readonly components: JsonObject[]; readonly screens: JsonObject[]; component(component: JsonObject): FrontendBuilder; screen(screen: JsonObject): FrontendBuilder; }
