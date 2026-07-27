from __future__ import annotations

import pytest

from codepotg_openapi.options import OpenApiOptions, OptionDecodeError


def test_yaml_limits_decode_and_enter_canonical_identity() -> None:
    options = OpenApiOptions.decode(
        (("maxYamlDepth", 9), ("maxYamlNodes", 99), ("maxYamlAliases", 7))
    )
    assert options.max_yaml_depth == 9
    assert options.max_yaml_nodes == 99
    assert options.max_yaml_aliases == 7
    canonical = dict(options.canonical_items())
    assert canonical["maxYamlDepth"] == 9
    assert canonical["maxYamlNodes"] == 99
    assert canonical["maxYamlAliases"] == 7


@pytest.mark.parametrize("key", ["maxYamlDepth", "maxYamlNodes", "maxYamlAliases"])
def test_yaml_limits_must_be_positive_integers(key: str) -> None:
    for value in (0, -1, True, "10"):
        with pytest.raises(OptionDecodeError):
            OpenApiOptions.decode(((key, value),))
