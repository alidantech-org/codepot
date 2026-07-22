/**
 * Public entry point for the new Codepot TypeScript package.
 *
 * Runtime authoring APIs will be added after the shared contracts are stable.
 */
export {
  CODEPOT_ARTIFACT_VERSION,
  CODEPOT_PROTOCOL_VERSION,
} from './contract/index';

export type * from './contract/index';
