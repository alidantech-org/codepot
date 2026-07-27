from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field

from codepotg.ir import SemanticId

_SLUG = re.compile(r"[^A-Za-z0-9._-]+")


def stable_id(
    *,
    source: str,
    category: str,
    pointer: str,
    hint: str,
    explicit: str | None = None,
) -> SemanticId:
    if explicit is not None:
        return SemanticId(explicit)
    slug = _SLUG.sub("-", hint).strip("-._").lower() or category
    digest = hashlib.sha256(f"{source}\0{category}\0{pointer}".encode()).hexdigest()[:16]
    return SemanticId(f"oa:{category}:{slug}:{digest}")


@dataclass(slots=True)
class IdentityRegistry:
    _owners: dict[SemanticId, str] = field(default_factory=dict)

    def register(self, semantic_id: SemanticId, owner: str) -> str | None:
        previous = self._owners.get(semantic_id)
        if previous is None:
            self._owners[semantic_id] = owner
        return previous
