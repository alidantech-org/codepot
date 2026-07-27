from __future__ import annotations

import pytest

import codepotg
from codepotg.versions import BehaviorVersion, Version


def test_versions_parse_order_and_round_trip() -> None:
    alpha = Version.parse("2.0.0-alpha.1")
    beta = Version.parse("2.0.0-beta.1")
    release = Version.parse("2.0.0")

    assert alpha < beta < release
    assert str(alpha) == "2.0.0-alpha.1"
    assert codepotg.__version__ == str(codepotg.CORE_VERSION)


@pytest.mark.parametrize("value", ["", "1", "1.0", "v1.0.0", "1.0.-1"])
def test_versions_reject_invalid_values(value: str) -> None:
    with pytest.raises(ValueError):
        Version.parse(value)


def test_behavior_versions_start_at_one() -> None:
    assert str(BehaviorVersion(1)) == "1"
    with pytest.raises(ValueError):
        BehaviorVersion(0)
