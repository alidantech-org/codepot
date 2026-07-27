from __future__ import annotations

from dataclasses import dataclass

from .builtins import builtin_descriptors
from .descriptors import HelperDescriptor, HelperKind


class HelperConflictError(ValueError):
    def __init__(self, name: str) -> None:
        super().__init__(f"duplicate Jinja helper name: {name}")
        self.name = name


@dataclass(frozen=True, slots=True)
class RegisteredCallable:
    descriptor: HelperDescriptor

    def __call__(self, *args: object, **kwargs: object) -> object:
        return self.descriptor.implementation(*args, **kwargs)


@dataclass(frozen=True, slots=True)
class HelperRegistry:
    descriptors: tuple[HelperDescriptor, ...]

    @classmethod
    def create(
        cls,
        custom: tuple[HelperDescriptor, ...] = (),
    ) -> HelperRegistry:
        entries = (*builtin_descriptors(), *custom)
        seen: set[str] = set()
        for entry in entries:
            if entry.name in seen:
                raise HelperConflictError(entry.name)
            seen.add(entry.name)
        return cls(tuple(sorted(entries, key=HelperDescriptor.identity)))

    @property
    def identity(self) -> tuple[tuple[str, str, str, str], ...]:
        return tuple(item.identity() for item in self.descriptors)

    def filters(self) -> dict[str, object]:
        return {
            item.name: item.implementation
            for item in self.descriptors
            if item.kind is HelperKind.FILTER
        }

    def tests(self) -> dict[str, object]:
        return {
            item.name: item.implementation
            for item in self.descriptors
            if item.kind is HelperKind.TEST
        }

    def globals(self) -> dict[str, object]:
        return {
            item.name: RegisteredCallable(item)
            for item in self.descriptors
            if item.kind is HelperKind.GLOBAL
        }
