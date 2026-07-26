from __future__ import annotations

import re
from dataclasses import dataclass
from functools import total_ordering

_SEMVER_PATTERN = re.compile(
    r"^(?P<major>0|[1-9]\d*)\."
    r"(?P<minor>0|[1-9]\d*)\."
    r"(?P<patch>0|[1-9]\d*)"
    r"(?:-(?P<prerelease>[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?"
    r"(?:\+(?P<build>[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$"
)


@total_ordering
@dataclass(frozen=True, slots=True)
class Version:
    """A small, dependency-free Semantic Version value object."""

    major: int
    minor: int
    patch: int
    prerelease: tuple[str, ...] = ()
    build: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if min(self.major, self.minor, self.patch) < 0:
            raise ValueError("version components must be non-negative")
        for identifier in (*self.prerelease, *self.build):
            if not identifier or not re.fullmatch(r"[0-9A-Za-z-]+", identifier):
                raise ValueError(f"invalid semantic-version identifier: {identifier!r}")

    @classmethod
    def parse(cls, value: str) -> Version:
        match = _SEMVER_PATTERN.fullmatch(value.strip())
        if match is None:
            raise ValueError(f"invalid semantic version: {value!r}")
        prerelease = tuple(filter(None, (match.group("prerelease") or "").split(".")))
        build = tuple(filter(None, (match.group("build") or "").split(".")))
        return cls(
            major=int(match.group("major")),
            minor=int(match.group("minor")),
            patch=int(match.group("patch")),
            prerelease=prerelease,
            build=build,
        )

    def __str__(self) -> str:
        value = f"{self.major}.{self.minor}.{self.patch}"
        if self.prerelease:
            value += "-" + ".".join(self.prerelease)
        if self.build:
            value += "+" + ".".join(self.build)
        return value

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Version):
            return NotImplemented
        left = (self.major, self.minor, self.patch)
        right = (other.major, other.minor, other.patch)
        if left != right:
            return left < right
        return _compare_prerelease(self.prerelease, other.prerelease) < 0

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Version):
            return False
        return (
            self.major,
            self.minor,
            self.patch,
            self.prerelease,
        ) == (
            other.major,
            other.minor,
            other.patch,
            other.prerelease,
        )


def _compare_prerelease(left: tuple[str, ...], right: tuple[str, ...]) -> int:
    if left == right:
        return 0
    if not left:
        return 1
    if not right:
        return -1
    for left_part, right_part in zip(left, right, strict=False):
        if left_part == right_part:
            continue
        left_numeric = left_part.isdigit()
        right_numeric = right_part.isdigit()
        if left_numeric and right_numeric:
            return -1 if int(left_part) < int(right_part) else 1
        if left_numeric != right_numeric:
            return -1 if left_numeric else 1
        return -1 if left_part < right_part else 1
    return -1 if len(left) < len(right) else 1


@dataclass(frozen=True, slots=True)
class ApiVersion:
    """Version of one public contract family."""

    family: str
    version: Version

    def __post_init__(self) -> None:
        if not self.family or not self.family.strip():
            raise ValueError("API version family must not be empty")

    @classmethod
    def parse(cls, family: str, value: str) -> ApiVersion:
        return cls(family=family.strip(), version=Version.parse(value))


@dataclass(frozen=True, slots=True)
class BehaviorVersions:
    """Independent behavior versions that participate in plan/cache identity."""

    naming: int = 1
    selection: int = 1
    planning: int = 1

    def __post_init__(self) -> None:
        if min(self.naming, self.selection, self.planning) < 1:
            raise ValueError("behavior versions start at 1")


CORE_VERSION = Version.parse("2.0.0-alpha.1")
PUBLIC_API_VERSION = ApiVersion("codepotg.public", Version.parse("2.0.0"))
IR_API_VERSION = ApiVersion("codepotg.ir", Version.parse("2.0.0"))
PLUGIN_API_VERSION = ApiVersion("codepotg.plugin", Version.parse("1.0.0"))
DEFAULT_BEHAVIOR_VERSIONS = BehaviorVersions()
