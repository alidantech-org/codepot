import type { JsonObject } from '@/contract/index';
import type { VersionBuilder, VersionContract } from '../version/version.types';
export interface CodepotConfig { readonly contracts: readonly (VersionBuilder | VersionContract)[]; readonly metadata?: JsonObject; }
export type PackageConfig = CodepotConfig;
