import type { CodepotConfig, PackageConfig } from './config.types';
export function defineCodepotConfig<const TConfig extends CodepotConfig>(config: TConfig): TConfig { return Object.freeze(config); }
/** @deprecated Use defineCodepotConfig. */
export function definePackageConfig<const TConfig extends PackageConfig>(config: TConfig): TConfig { return defineCodepotConfig(config); }
export function isCodepotConfig(value: unknown): value is CodepotConfig { return Boolean(value && typeof value === 'object' && Array.isArray((value as { contracts?: unknown }).contracts)); }
