from __future__ import annotations

from dataclasses import dataclass, field

from .identity import ReferenceIdentity


@dataclass(slots=True)
class ReferenceGraph:
    _edges: dict[ReferenceIdentity, set[ReferenceIdentity]] = field(default_factory=dict)

    def add(self, source: ReferenceIdentity, target: ReferenceIdentity) -> bool:
        self._edges.setdefault(source, set()).add(target)
        return self._reaches(target, source, set())

    def _reaches(
        self,
        current: ReferenceIdentity,
        target: ReferenceIdentity,
        seen: set[ReferenceIdentity],
    ) -> bool:
        if current == target:
            return True
        if current in seen:
            return False
        seen.add(current)
        return any(self._reaches(item, target, seen) for item in self._edges.get(current, ()))
