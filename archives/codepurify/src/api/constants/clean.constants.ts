export const CLEAN_ACTION = {
  name: 'clean',
} as const;

export const CLEAN_LOG_MESSAGES = {
  starting: 'Starting clean operation...',
  completed: 'Clean completed successfully',
  cacheNotFound: 'Cache directory does not exist',
  nothingToClean: 'Nothing to clean',
  cacheCleared: 'Cache cleared successfully',
  cancelled: 'Clean cancelled',
} as const;

export const CLEAN_PATHS = {
  cacheDir: '.codepurify/cache',
} as const;
