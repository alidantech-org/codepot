/** Public entry point for Codepot authoring and shared contracts. */
export {
  schema,
  SchemaKind,
  z,
  ZOD_COMPATIBILITY_FEATURES,
} from './authoring/index';

export type * from './authoring/index';

export {
  CODEPOT_ARTIFACT_VERSION,
  CODEPOT_PROTOCOL_VERSION,
} from './contract/index';

export type * from './contract/index';
