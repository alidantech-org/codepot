import type { CodepurifyFileDb } from './file-db';
import type { CodepurifyFileReader } from './file-reader';
import type { CodepurifyFileValidationResult } from './file-types';

export class CodepurifyFileValidator {
  constructor(
    private readonly db: CodepurifyFileDb,
    private readonly reader: CodepurifyFileReader,
  ) {}

  async validate(): Promise<CodepurifyFileValidationResult[]> {
    const records = await this.db.list();
    const results: CodepurifyFileValidationResult[] = [];

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
