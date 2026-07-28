from __future__ import annotations

import pytest
from dryv.api import OperationStatus

from dryv_cli.services import operation_exit_code


@pytest.mark.parametrize(
    ("status", "expected"),
    [
        (OperationStatus.READY, 0),
        (OperationStatus.GENERATED, 0),
        (OperationStatus.GENERATED_WITH_WARNINGS, 0),
        (OperationStatus.GENERATED_WITH_ACTIONS, 0),
        (OperationStatus.PARTIALLY_GENERATED, 0),
        (OperationStatus.FAILED, 1),
        (OperationStatus.CANCELLED, 130),
    ],
)
def test_operation_exit_code(status: OperationStatus, expected: int) -> None:
    assert operation_exit_code(status) == expected
