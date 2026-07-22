import { randomUUID } from 'node:crypto';
import { performance } from 'node:perf_hooks';

import type { ClockPort, IdPort, IsoTimestamp } from '@/contract/index';

export class SystemClock implements ClockPort {
  now(): IsoTimestamp {
    return new Date().toISOString();
  }

  monotonicMilliseconds(): number {
    return performance.now();
  }
}

export class FixedClock implements ClockPort {
  #current: number;

  constructor(timestamp: IsoTimestamp | number) {
    this.#current = typeof timestamp === 'number' ? timestamp : Date.parse(timestamp);
  }

  now(): IsoTimestamp {
    return new Date(this.#current).toISOString();
  }

  monotonicMilliseconds(): number {
    return this.#current;
  }

  advance(milliseconds: number): void {
    this.#current += milliseconds;
  }
}

export class RandomIdProvider implements IdPort {
  create(prefix?: string): string {
    const id = randomUUID();
    return prefix ? `${prefix}_${id}` : id;
  }
}

export class SequentialIdProvider implements IdPort {
  #next = 1;

  create(prefix = 'id'): string {
    const value = `${prefix}_${String(this.#next).padStart(4, '0')}`;
    this.#next += 1;
    return value;
  }
}
