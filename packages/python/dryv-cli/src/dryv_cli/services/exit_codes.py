from __future__ import annotations

from dryv.api import OperationStatus


def operation_exit_code(status: OperationStatus) -> int:
    if status is OperationStatus.CANCELLED:
        return 130
    if status is OperationStatus.FAILED:
        return 1
    return 0
