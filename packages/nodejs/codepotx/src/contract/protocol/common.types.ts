/** JSON-compatible primitives used by stable Codepot artifacts. */
export type JsonPrimitive = string | number | boolean | null;

/** A recursively JSON-serializable value. */
export type JsonValue =
  | JsonPrimitive
  | readonly JsonValue[]
  | { readonly [key: string]: JsonValue };

/** A JSON-serializable object with immutable values. */
export type JsonObject = Readonly<Record<string, JsonValue>>;

/** A path represented without binding the contract to a concrete filesystem API. */
export type PortablePath = string;

/** A URI represented as a string. */
export type UriString = string;

/** A deterministic content digest such as a SHA-256 value. */
export type ContentDigest = string;

/** An ISO-8601 timestamp. */
export type IsoTimestamp = string;

/** A stable identifier scoped by the artifact or runtime that owns it. */
export type CodepotId = string;

/** A value that may be returned immediately or asynchronously. */
export type Awaitable<T> = T | PromiseLike<T>;

/** A resource that can release subscriptions or other runtime state. */
export interface Disposable {
  dispose(): Awaitable<void>;
}

/** Platform-neutral cancellation signal injected into long-running operations. */
export interface CancellationSignal {
  readonly aborted: boolean;
  readonly reason?: string;

  throwIfAborted(): void;

  subscribe(listener: () => void): Disposable;
}
