/**
 * File Action Types
 *
 * Type-safe enums for file actions in Codepurify operations.
 */

/**
 * File action enum for type safety.
 */
export enum FileAction {
  CREATED = 'created',
  UPDATED = 'updated',
  UNCHANGED = 'unchanged',
  DELETED = 'deleted',
}

/**
 * Type guard to check if a string is a valid FileAction.
 */
export function isValidFileAction(action: string): action is FileAction {
  return Object.values(FileAction).includes(action as FileAction);
}
