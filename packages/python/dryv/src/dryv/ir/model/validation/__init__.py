from __future__ import annotations

from dryv.diagnostics import Diagnostics

from ..groups import Contract
from .additional import validate_additional_contract
from .index import SemanticIndex
from .validator import ContractValidator as _BaseContractValidator


class ContractValidator(_BaseContractValidator):
    def validate(self, contract: Contract) -> Diagnostics:
        base = super().validate(contract)
        index, _ = SemanticIndex.build(contract)
        return base.extend(validate_additional_contract(contract, index))


def validate_contract(contract: Contract) -> Diagnostics:
    return ContractValidator().validate(contract)


__all__ = ["ContractValidator", "SemanticIndex", "validate_contract"]
