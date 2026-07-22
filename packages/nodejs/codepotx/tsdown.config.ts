import { defineConfig } from 'tsdown';

export default defineConfig({
  entry: 'src/index.ts',
  outDir: 'dist',
  format: ['esm'],
  platform: 'node',
  target: 'node22',
  tsconfig: 'tsconfig.json',
  dts: {
    sourcemap: true,
  },
  sourcemap: true,
  clean: true,
  minify: false,
  report: true,
});
