/**
 * File Constants
 *
 * Constants and helpers for Codepurify file operations.
 */

export const FILE_DB_CONSTANTS = {
  /**
   * Default database file name.
   */
  defaultFileName: '.codepurify/files.json',

  /**
   * Database version.
   */
  version: 1,

  /**
   * Database generator identifier.
   */
  generator: 'codepurify',

  /**
   * Temporary file suffix for atomic writes.
   */
  tempSuffix: '.tmp',

  /**
   * JSON formatting options.
   */
  jsonFormat: {
    indent: 2,
    finalNewline: true,
  },
} as const;

export const FILE_BACKUP_CONSTANTS = {
  /**
   * Default backup directory name.
   */
  defaultDirName: '.codepurify/backups',

  /**
   * Session file name.
   */
  sessionFileName: 'session.json',

  /**
   * Session ID prefix.
   */
  sessionIdPrefix: 'backup_',

  /**
   * JSON formatting options for session files.
   */
  jsonFormat: {
    indent: 2,
    finalNewline: true,
  },
} as const;

/**
 * Helper function to create a temporary file path for atomic writes.
 */
export function createTempFilePath(dbPath: string): string {
  return `${dbPath}${FILE_DB_CONSTANTS.tempSuffix}.${Date.now()}`;
}

/**
 * Helper function to format database JSON content.
 */
export function formatDbJson(db: any): string {
  const json = JSON.stringify(db, null, FILE_DB_CONSTANTS.jsonFormat.indent);
  return FILE_DB_CONSTANTS.jsonFormat.finalNewline ? json + '\n' : json;
}

/**
 * Helper function to create an empty database structure.
 */
export function createEmptyFileDb() {
  return {
    version: FILE_DB_CONSTANTS.version,
    generator: FILE_DB_CONSTANTS.generator,
    updatedAt: null,
    records: [],
  };
}

/**
 * Helper function to create a backup session ID.
 */
export function createBackupSessionId(): string {
  return `${FILE_BACKUP_CONSTANTS.sessionIdPrefix}${new Date().toISOString().replace(/[:.]/g, '-')}_${Math.random().toString(36).slice(2, 8)}`;
}

/**
 * Helper function to format backup session JSON content.
 */
export function formatBackupSessionJson(session: any): string {
  const json = JSON.stringify(session, null, FILE_BACKUP_CONSTANTS.jsonFormat.indent);
  return FILE_BACKUP_CONSTANTS.jsonFormat.finalNewline ? json + '\n' : json;
}
