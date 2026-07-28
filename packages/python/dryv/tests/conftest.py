from __future__ import annotations

import pytest

from dryv.ir import Contract
from tests.fixtures import build_connected_contract


@pytest.fixture
def connected_contract() -> Contract:
    return build_connected_contract()
