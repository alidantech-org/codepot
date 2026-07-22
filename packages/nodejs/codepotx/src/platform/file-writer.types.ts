import type { FileSystemPort, PortablePath } from '@/contract/index';

/** Platform-internal filesystem capability required for atomic replacement. */
export interface AtomicFileSystemPort extends FileSystemPort {
  move(
    from: PortablePath,
    to: PortablePath,
    options?: { readonly overwrite?: boolean },
  ): Promise<void>;
}
