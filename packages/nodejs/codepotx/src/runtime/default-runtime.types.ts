import type { CodepotRuntimePort } from '@/contract/index';
import type { DefaultPlatformOptions, PlatformServices } from '@/platform/index';

export interface DefaultCodepotRuntimeOptions extends DefaultPlatformOptions {
  readonly platform?: PlatformServices;
}

export interface DefaultCodepotRuntimeComposition {
  readonly runtime: CodepotRuntimePort;
  readonly platform: PlatformServices;
}
