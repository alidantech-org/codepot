from __future__ import annotations

from dataclasses import dataclass, replace
from enum import StrEnum
from pathlib import Path, PurePosixPath


class VirtualOutputConflictError(RuntimeError):
    """Raised when virtual outputs are duplicate, ambiguous, unsafe, or unbounded."""


class OutputStatus(StrEnum):
    """Lifecycle state stored in the in-memory output registry."""

    PLANNED = "planned"
    WRITTEN = "written"


@dataclass(frozen=True, slots=True)
class OutputRegistryLimits:
    """Correctness-preserving registry bound; entries are never silently evicted."""

    max_entries: int = 500_000


@dataclass(frozen=True, slots=True)
class VirtualOutput:
    """One output known before its physical file exists."""

    selection: str
    emission: str
    source_key: str
    source_ref: str | None
    template_path: PurePosixPath
    output_path: PurePosixPath
    symbols: tuple[str, ...] = ()
    provides: tuple[str, ...] = ()
    resource: str | None = None
    status: OutputStatus = OutputStatus.PLANNED

    @property
    def identity(self) -> tuple[str, str, str]:
        return self.selection, self.emission, self.source_key

    def to_json(self) -> dict[str, object]:
        return {
            "selection": self.selection,
            "emission": self.emission,
            "sourceKey": self.source_key,
            "sourceRef": self.source_ref,
            "template": self.template_path.as_posix(),
            "file": self.output_path.as_posix(),
            "symbols": list(self.symbols),
            "provides": list(self.provides),
            "resource": self.resource,
            "status": self.status.value,
        }


class VirtualOutputRegistry:
    """Deterministic planned/written file registry used by import resolution."""

    def __init__(self, limits: OutputRegistryLimits | None = None) -> None:
        self._limits = limits or OutputRegistryLimits()
        if self._limits.max_entries < 1:
            raise ValueError("max_entries must be at least 1")
        self._by_identity: dict[tuple[str, str, str], VirtualOutput] = {}
        self._by_path: dict[str, tuple[str, str, str]] = {}
        self._by_ref: dict[str, set[tuple[str, str, str]]] = {}
        self._by_source: dict[str, set[tuple[str, str, str]]] = {}
        self._by_emission: dict[str, set[tuple[str, str, str]]] = {}

    def register(
        self,
        *,
        selection: str,
        emission: str,
        source_key: str,
        source_ref: str | None,
        template_path: str | Path | PurePosixPath,
        output_path: str | Path | PurePosixPath,
        symbols: tuple[str, ...] = (),
        provides: tuple[str, ...] = (),
        resource: str | None = None,
    ) -> VirtualOutput:
        if not selection or not emission or not source_key:
            raise VirtualOutputConflictError(
                "selection, emission, and source_key must be non-empty"
            )

        template = normalize_registry_path(template_path, field="template")
        output = normalize_registry_path(output_path, field="output")
        normalized_symbols = tuple(sorted(set(symbol for symbol in symbols if symbol)))
        normalized_provides = tuple(sorted(set(value for value in provides if value)))
        item = VirtualOutput(
            selection=selection,
            emission=emission,
            source_key=source_key,
            source_ref=source_ref,
            template_path=template,
            output_path=output,
            symbols=normalized_symbols,
            provides=normalized_provides,
            resource=resource,
        )
        identity = item.identity
        if identity in self._by_identity:
            raise VirtualOutputConflictError(
                "Virtual output was planned more than once: "
                f"selection={selection}, emission={emission}, source={source_key}"
            )
        if len(self._by_identity) >= self._limits.max_entries:
            raise VirtualOutputConflictError(
                f"Virtual output registry exceeded {self._limits.max_entries} entries"
            )

        path_key = output.as_posix()
        existing_identity = self._by_path.get(path_key)
        if existing_identity is not None:
            existing = self._by_identity[existing_identity]
            raise VirtualOutputConflictError(
                f"Output path collision at '{path_key}' between "
                f"{existing.emission}:{existing.source_key} and {emission}:{source_key}"
            )

        self._by_identity[identity] = item
        self._by_path[path_key] = identity
        self._by_source.setdefault(source_key, set()).add(identity)
        self._by_emission.setdefault(emission, set()).add(identity)
        if source_ref:
            self._by_ref.setdefault(source_ref, set()).add(identity)
        return item

    def mark_written(
        self,
        *,
        selection: str,
        emission: str,
        source_key: str,
    ) -> VirtualOutput:
        identity = selection, emission, source_key
        return self._mark_identity_written(identity)

    def mark_written_path(self, output_path: str | Path | PurePosixPath) -> VirtualOutput:
        """Mark a registered output written using its portable path."""

        path = normalize_registry_path(output_path, field="output").as_posix()
        identity = self._by_path.get(path)
        if identity is None:
            raise VirtualOutputConflictError(
                f"Cannot mark an unknown virtual output written: {path}"
            )
        return self._mark_identity_written(identity)

    def get(
        self,
        *,
        selection: str,
        emission: str,
        source_key: str,
    ) -> VirtualOutput | None:
        return self._by_identity.get((selection, emission, source_key))

    def get_by_path(self, output_path: str | Path | PurePosixPath) -> VirtualOutput | None:
        """Return one registered output by portable path."""

        path = normalize_registry_path(output_path, field="output").as_posix()
        identity = self._by_path.get(path)
        return self._by_identity.get(identity) if identity is not None else None

    def find_ref(
        self,
        ref: str,
        *,
        selection: str | None = None,
        emission: str | None = None,
        written_only: bool = False,
    ) -> tuple[VirtualOutput, ...]:
        identities = self._by_ref.get(ref, set())
        return self._filter(
            identities,
            selection=selection,
            emission=emission,
            written_only=written_only,
        )

    def find_source(
        self,
        source_key: str,
        *,
        selection: str | None = None,
        emission: str | None = None,
        written_only: bool = False,
    ) -> tuple[VirtualOutput, ...]:
        identities = self._by_source.get(source_key, set())
        return self._filter(
            identities,
            selection=selection,
            emission=emission,
            written_only=written_only,
        )

    def find_emission(
        self,
        emission: str,
        *,
        resource: str | None = None,
        written_only: bool = False,
    ) -> tuple[VirtualOutput, ...]:
        """Return all outputs belonging to one emission node."""

        identities = self._by_emission.get(emission, set())
        values = self._filter(
            identities,
            selection=None,
            emission=emission,
            written_only=written_only,
        )
        if resource is None:
            return values
        return tuple(item for item in values if item.resource == resource)

    def snapshot(self, *, written_only: bool = False) -> tuple[VirtualOutput, ...]:
        values = tuple(self._by_identity.values())
        if written_only:
            values = tuple(
                item for item in values if item.status == OutputStatus.WRITTEN
            )
        return tuple(sorted(values, key=_sort_key))

    def __len__(self) -> int:
        return len(self._by_identity)

    def _mark_identity_written(
        self,
        identity: tuple[str, str, str],
    ) -> VirtualOutput:
        current = self._by_identity.get(identity)
        if current is None:
            raise VirtualOutputConflictError(
                f"Cannot mark an unknown virtual output written: {identity}"
            )
        if current.status == OutputStatus.WRITTEN:
            return current
        written = replace(current, status=OutputStatus.WRITTEN)
        self._by_identity[identity] = written
        return written

    def _filter(
        self,
        identities: set[tuple[str, str, str]],
        *,
        selection: str | None,
        emission: str | None,
        written_only: bool,
    ) -> tuple[VirtualOutput, ...]:
        values = tuple(
            self._by_identity[identity]
            for identity in identities
            if (selection is None or identity[0] == selection)
            and (emission is None or identity[1] == emission)
        )
        if written_only:
            values = tuple(
                item for item in values if item.status == OutputStatus.WRITTEN
            )
        return tuple(sorted(values, key=_sort_key))


def normalize_registry_path(
    value: str | Path | PurePosixPath,
    *,
    field: str,
) -> PurePosixPath:
    """Normalize authored paths to portable relative POSIX paths."""

    text = str(value).replace("\\", "/").strip()
    if not text:
        raise VirtualOutputConflictError(f"Virtual {field} path must be non-empty")
    if len(text) >= 2 and text[1] == ":":
        raise VirtualOutputConflictError(f"Virtual {field} path is unsafe: {value}")
    path = PurePosixPath(text)
    if path.is_absolute() or ".." in path.parts:
        raise VirtualOutputConflictError(f"Virtual {field} path is unsafe: {value}")
    parts = tuple(part for part in path.parts if part not in {"", "."})
    if not parts:
        raise VirtualOutputConflictError(f"Virtual {field} path must be non-empty")
    return PurePosixPath(*parts)


def _sort_key(item: VirtualOutput) -> tuple[str, str, str, str]:
    return (
        item.output_path.as_posix(),
        item.selection,
        item.emission,
        item.source_key,
    )
