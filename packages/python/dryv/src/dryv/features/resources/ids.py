from __future__ import annotations

from dataclasses import dataclass


class ResourceIdError(ValueError):
    pass


@dataclass(frozen=True, slots=True, order=True)
class ResourceId:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", normalize_resource_id(self.value))

    @property
    def namespace(self) -> str:
        return self.value.removeprefix("resource://").split("/", 1)[0]

    @property
    def path(self) -> str:
        remainder = self.value.removeprefix("resource://")
        return remainder.split("/", 1)[1]

    def __str__(self) -> str:
        return self.value


def normalize_resource_id(value: str | ResourceId) -> str:
    if isinstance(value, ResourceId):
        return value.value
    if not isinstance(value, str) or value.strip() != value:
        raise ResourceIdError("resource id must be a trimmed string")
    if not value.startswith("resource://"):
        raise ResourceIdError("resource id must use the resource:// scheme")
    if "\\" in value or "?" in value or "#" in value:
        raise ResourceIdError("resource id cannot contain host path separators, query, or fragment")
    remainder = value.removeprefix("resource://")
    if "/" not in remainder:
        raise ResourceIdError("resource id requires a namespace and relative path")
    namespace, path = remainder.split("/", 1)
    if not namespace or namespace in {".", ".."} or any(character.isspace() for character in namespace):
        raise ResourceIdError("resource namespace must be a non-empty identifier")
    parts = path.split("/")
    if any(not part or part in {".", ".."} for part in parts):
        raise ResourceIdError("resource path cannot contain empty, dot, or traversal segments")
    if any(any(character.isspace() for character in part) for part in parts):
        raise ResourceIdError("resource path segments cannot contain whitespace")
    return f"resource://{namespace}/{'/'.join(parts)}"


def resource_id(namespace: str, relative_name: str) -> ResourceId:
    if not namespace or "/" in namespace or "\\" in namespace:
        raise ResourceIdError("resource namespace must be one path segment")
    relative = relative_name.replace("\\", "/")
    return ResourceId(f"resource://{namespace}/{relative}")


__all__ = ["ResourceId", "ResourceIdError", "normalize_resource_id", "resource_id"]
