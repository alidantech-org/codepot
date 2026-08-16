from __future__ import annotations

from dryv.ir import Contract, validate_contract
from dryv.ir.diagnostics import Diagnostics


def validate_ir(contract: Contract) -> Diagnostics:
    return validate_contract(contract)


__all__ = ["validate_ir"]
