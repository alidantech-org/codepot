import { spawn } from 'node:child_process';
import type { CommandRequest, CommandResult, CommandRunnerPort } from '@/contract/index';
import { OperationCancelledError, PlatformOperationError } from '../shared/errors';

export class NodeCommandRunner implements CommandRunnerPort {
  async run(request: CommandRequest): Promise<CommandResult> {
    request.signal?.throwIfAborted();
    if (request.dryRun) {
      return {
        command: request.command,
        cwd: request.cwd,
        exitCode: null,
        stdout: '',
        stderr: '',
        skipped: true,
      };
    }
    return new Promise<CommandResult>((resolve, reject) => {
      const processHandle = spawn(request.command, {
        cwd: request.cwd,
        env: { ...process.env, ...request.environment },
        shell: true,
        stdio: ['ignore', 'pipe', 'pipe'],
        windowsHide: true,
        detached: process.platform !== 'win32',
      });
      const stdout: Buffer[] = [];
      const stderr: Buffer[] = [];
      let cancelled = false;
      const subscription = request.signal?.subscribe(() => {
        cancelled = true;
        if (process.platform === 'win32' && processHandle.pid) {
          const killer = spawn('taskkill', ['/pid', String(processHandle.pid), '/T', '/F'], {
            stdio: 'ignore',
            windowsHide: true,
          });
          killer.unref();
          return;
        }
        if (processHandle.pid) {
          try {
            process.kill(-processHandle.pid, 'SIGTERM');
            return;
          } catch {
            // Fall back to terminating only the shell process.
          }
        }
        processHandle.kill();
      });
      processHandle.stdout.on('data', (chunk: Buffer) => stdout.push(chunk));
      processHandle.stderr.on('data', (chunk: Buffer) => stderr.push(chunk));
      processHandle.once('error', (caught) => {
        subscription?.dispose();
        reject(new PlatformOperationError(
          'COMMAND_START_FAILED',
          `Command could not start: ${request.command}`,
          { cause: caught },
        ));
      });
      processHandle.once('close', (exitCode) => {
        subscription?.dispose();
        if (cancelled) {
          reject(new OperationCancelledError(request.signal?.reason));
          return;
        }
        resolve({
          command: request.command,
          cwd: request.cwd,
          exitCode,
          stdout: Buffer.concat(stdout).toString('utf8'),
          stderr: Buffer.concat(stderr).toString('utf8'),
          skipped: false,
        });
      });
    });
  }
}
