import { definecodepotConfig } from 'codepot';

export default definecodepotConfig({
  rootDir: process.cwd(),
  outputDir: './src/generated',
  manifestPath: './codepot/manifest.json',

  // Config directories with dynamic inference
  entitiesDir: '__codepot_ENTITIES_DIR__',
  resourcesDir: '__codepot_RESOURCES_DIR__',
});
