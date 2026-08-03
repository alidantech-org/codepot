# codepot Files Module

Drop this folder into:

```txt
src/core/files/
```

Then export it from your core barrel:

```ts
export * from './files';
```

Use it inside your runtime:

```ts
import { codepotFiles } from '@/core/files';

export class codepotRuntime {
  readonly files: codepotFiles;

  constructor(options: codepotOptions = {}) {
    this.files = new codepotFiles({
      rootDir: this.cwd,
      dbPath: '.codepot/files.json',
      backupDir: '.codepot/backups',
    });
  }
}
```

Generation should call:

```ts
await runtime.files.writeGenerated({
  path: outputPath,
  content,
  source: entityConfigPath,
  template: template.name,
  immutable: false,
});
```

Rollback should call:

```ts
await runtime.files.rollbackLatest();
```

The old `ManifestManager` concept is replaced by `codepotFileDb`, which is the JSON DB behind `codepotFiles`.
