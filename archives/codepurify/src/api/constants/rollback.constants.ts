export const ROLLBACK_ACTION = {
  name: 'rollback',
} as const;

export const ROLLBACK_LOG_MESSAGES = {
  starting: 'Starting rollback operation...',
  completed: (backupId: string) => `Rollback completed successfully from backup: ${backupId}`,
  restored: (count: number) => `Restored ${count} file(s).`,
  deleted: (count: number) => `Deleted ${count} generated file(s).`,
  skipped: (count: number) => `Skipped ${count} file(s).`,
} as const;
