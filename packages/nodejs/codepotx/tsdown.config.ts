import { defineConfig } from 'tsdown';

export default defineConfig({
  entry: [
    'src/index.ts',
    'src/contract/index.ts',
    'src/runtime/index.ts',
    'src/platform/index.ts',
    'src/authoring/index.ts',
    'src/templating/index.ts',
  ],
  root: 'src',
  outDir: 'dist',
  format: ['esm'],
  platform: 'node',
  target: 'node22',
  tsconfig: 'tsconfig.json',
  dts: { sourcemap: true },
  sourcemap: true,
  clean: true,
  minify: false,
  report: true,
});
