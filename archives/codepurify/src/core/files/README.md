# Codepurify Files Module

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
import { CodepurifyFiles } from '@/core/files';

export class CodepurifyRuntime {
  readonly files: CodepurifyFiles;

  constructor(options: CodepurifyOptions = {}) {
    this.files = new CodepurifyFiles({
      rootDir: this.cwd,
      dbPath: '.codepurify/files.json',
      backupDir: '.codepurify/backups',
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

The old `ManifestManager` concept is replaced by `CodepurifyFileDb`, which is the JSON DB behind `CodepurifyFiles`.
