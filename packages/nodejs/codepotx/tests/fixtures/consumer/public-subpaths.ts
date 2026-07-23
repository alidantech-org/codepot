import {
  defineCodepotConfig,
  defineVersionContract,
  z,
} from 'codepotx';
import {
  CODEPOT_ARTIFACT_VERSION,
  CODEPOT_PROTOCOL_VERSION,
  type CompiledAuthoringArtifact,
} from 'codepotx/contract';
import {
  DefaultAuthoringCompiler,
} from 'codepotx/authoring';
import {
  createGenerationEngine,
} from 'codepotx/generation';
import {
  createMemoryPlatformServices,
} from 'codepotx/platform';
import {
  createDefaultCodepotRuntime,
} from 'codepotx/runtime';
import {
  createTemplatingEngine,
} from 'codepotx/templating';

const version = defineVersionContract({
  info: { title: 'Consumer fixture', version: '1.0.0' },
});
const schemas = version.defineSchemas({
  User: {
    id: z.string(),
    name: z.string().min(1),
  },
});
const user = schemas.ref.User;
const config = defineCodepotConfig({ contracts: [version] });

// @ts-expect-error unknown schema refs must remain a compile-time error.
void schemas.ref.Missing;

void user;
void config;
void CODEPOT_ARTIFACT_VERSION;
void CODEPOT_PROTOCOL_VERSION;
void (undefined as CompiledAuthoringArtifact | undefined);
void DefaultAuthoringCompiler;
void createGenerationEngine;
void createMemoryPlatformServices;
void createDefaultCodepotRuntime;
void createTemplatingEngine;
