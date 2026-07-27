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
    major: int
    minor: int
    patch: int
    prerelease: tuple[str, ...] = ()
    build: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if min(self.major, self.minor, self.patch) < 0:
            raise ValueError("version components must be non-negative")
        for identifier in (*self.prerelease, *self.build):
            if not identifier or re.fullmatch(r"[0-9A-Za-z-]+", identifier) is None:
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
        release_comparison = (self.major, self.minor, self.patch), (
            other.major,
            other.minor,
            other.patch,
        )
        if release_comparison[0] != release_comparison[1]:
            return release_comparison[0] < release_comparison[1]
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


@dataclass(frozen=True, slots=True)
class ApiVersion:
    family: str
    version: Version

    def __post_init__(self) -> None:
        if not self.family or self.family.strip() != self.family:
            raise ValueError("API version family must be a non-empty trimmed string")

    @classmethod
    def parse(cls, family: str, value: str) -> ApiVersion:
        return cls(family=family, version=Version.parse(value))

    def __str__(self) -> str:
        return f"{self.family}/{self.version}"


@dataclass(frozen=True, slots=True)
class BehaviorVersion:
    value: int

    def __post_init__(self) -> None:
        if self.value < 1:
            raise ValueError("behavior versions start at 1")

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True, slots=True)
class BehaviorVersions:
    naming: BehaviorVersion = BehaviorVersion(1)
    selection: BehaviorVersion = BehaviorVersion(1)
    planning: BehaviorVersion = BehaviorVersion(1)


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
