import type { codepotFileDb } from './file-db';
import type { codepotFileReader } from './file-reader';
import type { codepotFileValidationResult } from './file-types';

export class codepotFileValidator {
  constructor(
    private readonly db: codepotFileDb,
    private readonly reader: codepotFileReader,
  ) {}

  async validate(): Promise<codepotFileValidationResult[]> {
    const records = await this.db.list();
    const results: codepotFileValidationResult[] = [];

    for (const record of records) {
      try {
        const read = await this.reader.read(record.path, { hash: true });

        results.push({
          record,
          exists: read.exists,
          hashMatches: read.hash ? read.hash === record.hash : false,
          actualHash: read.hash,
        });
      } catch (error) {
        results.push({
          record,
          exists: false,
          error: error instanceof Error ? error.message : String(error),
        });
      }
    }

    return results;
  }
}
