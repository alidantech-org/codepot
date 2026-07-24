import { RefKind } from "../refs/ref-kind.js";
import type {
  ComponentRef,
  EngineRef,
  PropertyRef,
} from "../refs/ref.types.js";

export function isEngineRef(value: unknown): value is EngineRef {
  if (!value || typeof value !== "object") return false;

  const ref = value as Partial<EngineRef>;

  return (
    typeof ref.id === "string" &&
    typeof ref.name === "string" &&
    typeof ref.kind === "string"
  );
}

export function isPropertyRef(value: unknown): value is PropertyRef {
  return isEngineRef(value) && value.kind === RefKind.property;
}

export function isComponentRef(value: unknown): value is ComponentRef {
  return isEngineRef(value) && value.kind === RefKind.component;
}
