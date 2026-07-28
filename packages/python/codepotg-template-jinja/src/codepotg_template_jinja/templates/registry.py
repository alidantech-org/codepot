from __future__ import annotations

import posixpath
import re
from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType

from codepotg.ports import RenderRequest
from codepotg_template_jinja.rules import JinjaEngineRules

_WINDOWS_DRIVE = re.compile(r"^[A-Za-z]:")


class TemplateRegistryError(ValueError):
    def __init__(
        self,
        code: str,
        message: str,
        *,
        template_id: str,
        details: tuple[tuple[str, object], ...] = (),
    ) -> None:
        super().__init__(message)
        self.code = code
        self.template_id = template_id
        self.details = details


@dataclass(frozen=True, slots=True)
class TemplateRegistry:
    root_id: str
    root_source: str
    partials: tuple[tuple[str, str], ...]
    _sources: Mapping[str, str]

    @classmethod
    def create(cls, request: RenderRequest, rules: JinjaEngineRules) -> TemplateRegistry:
        root_id = validate_template_id(request.template_id, rules, root=True)
        root_source = normalize_source(request.source, template_id=root_id, root=True)
        root_bytes = len(root_source.encode("utf-8"))
        if root_bytes > rules.max_template_bytes:
            raise TemplateRegistryError(
                "JINJA_TEMPLATE_TOO_LARGE",
                "root template exceeds the configured byte limit",
                template_id=root_id,
                details=(
                    ("actual_bytes", root_bytes),
                    ("max_bytes", rules.max_template_bytes),
                    ("template_id", root_id),
                ),
            )
        if len(request.partials) > rules.max_partial_count:
            raise TemplateRegistryError(
                "JINJA_PARTIAL_INVALID",
                "partial registry exceeds the configured count limit",
                template_id=root_id,
                details=(
                    ("actual_count", len(request.partials)),
                    ("max_count", rules.max_partial_count),
                    ("template_id", root_id),
                ),
            )

        partials: list[tuple[str, str]] = []
        total_partial_bytes = 0
        seen: set[str] = set()
        for partial_id, source in request.partials:
            validated_id = validate_template_id(partial_id, rules, root=False)
            if validated_id == root_id:
                raise TemplateRegistryError(
                    "JINJA_PARTIAL_INVALID",
                    "root template ID must not collide with a partial ID",
                    template_id=validated_id,
                    details=(
                        ("partial_id", validated_id),
                        ("template_id", root_id),
                    ),
                )
            if validated_id in seen:
                raise TemplateRegistryError(
                    "JINJA_PARTIAL_INVALID",
                    "partial IDs must be unique",
                    template_id=validated_id,
                    details=(("partial_id", validated_id),),
                )
            seen.add(validated_id)
            normalized = normalize_source(source, template_id=validated_id, root=False)
            partial_bytes = len(normalized.encode("utf-8"))
            if partial_bytes > rules.max_template_bytes:
                raise TemplateRegistryError(
                    "JINJA_TEMPLATE_TOO_LARGE",
                    "partial template exceeds the configured per-template byte limit",
                    template_id=validated_id,
                    details=(
                        ("actual_bytes", partial_bytes),
                        ("max_bytes", rules.max_template_bytes),
                        ("partial_id", validated_id),
                    ),
                )
            total_partial_bytes += partial_bytes
            if total_partial_bytes > rules.max_partial_bytes:
                raise TemplateRegistryError(
                    "JINJA_PARTIAL_INVALID",
                    "partial registry exceeds the configured total byte limit",
                    template_id=validated_id,
                    details=(
                        ("actual_bytes", total_partial_bytes),
                        ("max_bytes", rules.max_partial_bytes),
                        ("partial_id", validated_id),
                    ),
                )
            partials.append((validated_id, normalized))

        sorted_partials = tuple(sorted(partials))
        if tuple(partial_id for partial_id, _ in partials) != tuple(
            partial_id for partial_id, _ in sorted_partials
        ):
            raise TemplateRegistryError(
                "JINJA_PARTIAL_INVALID",
                "partial IDs must be sorted",
                template_id=root_id,
                details=(("template_id", root_id),),
            )
        sources = {root_id: root_source, **dict(sorted_partials)}
        return cls(
            root_id=root_id,
            root_source=root_source,
            partials=sorted_partials,
            _sources=MappingProxyType(sources),
        )

    @property
    def partial_ids(self) -> tuple[str, ...]:
        return tuple(partial_id for partial_id, _ in self.partials)

    def has_partial(self, template_id: str) -> bool:
        return template_id in self._sources and template_id != self.root_id

    def source(self, template_id: str) -> str:
        return self._sources[template_id]

    def selected(self, reachable_partial_ids: tuple[str, ...]) -> Mapping[str, str]:
        sources = {self.root_id: self.root_source}
        for partial_id in reachable_partial_ids:
            sources[partial_id] = self.source(partial_id)
        return MappingProxyType(sources)


def validate_template_id(
    value: object,
    rules: JinjaEngineRules,
    *,
    root: bool,
) -> str:
    code = "JINJA_TEMPLATE_ID_INVALID" if root else "JINJA_PARTIAL_INVALID"
    label = "template_id" if root else "partial_id"
    if not isinstance(value, str) or not value or value.strip() != value:
        raise TemplateRegistryError(
            code,
            f"{label} must be a non-empty trimmed string",
            template_id=value if isinstance(value, str) and value else "<invalid>",
            details=((label, repr(value)),),
        )
    try:
        encoded = value.encode("utf-8", errors="strict")
    except UnicodeEncodeError as exc:
        raise TemplateRegistryError(
            code,
            f"{label} must be valid UTF-8",
            template_id="<invalid>",
            details=((label, repr(value)),),
        ) from exc
    if len(encoded) > rules.max_template_id_length:
        raise TemplateRegistryError(
            code,
            f"{label} exceeds the configured length limit",
            template_id=value,
            details=(
                ("actual_bytes", len(encoded)),
                (label, value),
                ("max_bytes", rules.max_template_id_length),
            ),
        )
    if "\x00" in value or "\\" in value:
        raise TemplateRegistryError(
            code,
            f"{label} contains a forbidden NUL or backslash",
            template_id=value,
            details=((label, value),),
        )
    if value.startswith("/") or _WINDOWS_DRIVE.match(value):
        raise TemplateRegistryError(
            code,
            f"{label} must be a relative POSIX registry identifier",
            template_id=value,
            details=((label, value),),
        )
    segments = value.split("/")
    if any(segment in {"", ".", ".."} for segment in segments):
        raise TemplateRegistryError(
            code,
            f"{label} contains a non-normalized or traversal segment",
            template_id=value,
            details=((label, value),),
        )
    if posixpath.normpath(value) != value:
        raise TemplateRegistryError(
            code,
            f"{label} must use normalized POSIX-style segments",
            template_id=value,
            details=((label, value),),
        )
    return value


def normalize_source(source: object, *, template_id: str, root: bool) -> str:
    code = "JINJA_TEMPLATE_INVALID" if root else "JINJA_PARTIAL_INVALID"
    if not isinstance(source, str):
        raise TemplateRegistryError(
            code,
            "template source must be a string",
            template_id=template_id,
            details=(
                ("source_type", type(source).__name__),
                ("template_id", template_id),
            ),
        )
    normalized = source.replace("\r\n", "\n").replace("\r", "\n")
    try:
        normalized.encode("utf-8", errors="strict")
    except UnicodeEncodeError as exc:
        raise TemplateRegistryError(
            code,
            "template source must be valid UTF-8",
            template_id=template_id,
            details=(("template_id", template_id),),
        ) from exc
    return normalized
