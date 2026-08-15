from __future__ import annotations

from dryv.diagnostics import Diagnostic, Diagnostics

from ..groups import Contract
from ..operations import Operation
from .additional import validate_additional_contract
from .failures import validate_failures
from .index import SemanticIndex
from .properties import validate_property_contract
from .schema_extensions import validate_schema_extensions
from .validator import ContractValidator as _BaseContractValidator


class ContractValidator(_BaseContractValidator):
    def _validate_operation(self, operation: Operation, index: SemanticIndex, diagnostics: list[Diagnostic]) -> None:
        for item in operation.inputs:
            self._validate_schema_use(item, operation, index, diagnostics)
        for item in operation.outputs:
            self._validate_output(item, operation, index, diagnostics)
        for failure in operation.failures:
            self._require(failure, index.failures, "IR_MISSING_FAILURE", "operation failure", operation, diagnostics)
        self._validate_effects(operation.effects, operation, index, diagnostics)
        self._validate_operation_facets(operation.facets, operation, index, diagnostics)

    def validate(self, contract: Contract) -> Diagnostics:
        base = super().validate(contract)
        index, _ = SemanticIndex.build(contract)
        return base.extend(validate_property_contract(contract, index)).extend(validate_schema_extensions(contract, index)).extend(validate_failures(contract, index)).extend(validate_additional_contract(contract, index))


def validate_contract(contract: Contract) -> Diagnostics:
    return ContractValidator().validate(contract)


__all__ = ["ContractValidator", "SemanticIndex", "validate_contract"]
