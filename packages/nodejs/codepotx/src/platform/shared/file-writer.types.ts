import type { FileSystemPort, PortablePath } from '@/contract/index';

export interface AtomicFileSystemPort extends FileSystemPort {
  move(
    from: PortablePath,
    to: PortablePath,
    options?: { readonly overwrite?: boolean },
  ): Promise<void>;
}
