export const CODEPOT_PACKAGE_NAME = 'codepotx' as const;
export const CODEPOT_PACKAGE_VERSION = '0.0.0' as const;

export type CodepotArtifactProducerInfo = Readonly<{
  name: typeof CODEPOT_PACKAGE_NAME;
  version: typeof CODEPOT_PACKAGE_VERSION;
}>;

export const CODEPOT_ARTIFACT_PRODUCER: CodepotArtifactProducerInfo = {
  name: CODEPOT_PACKAGE_NAME,
  version: CODEPOT_PACKAGE_VERSION,
};
