from __future__ import annotations

from dryv.diagnostics import Diagnostic, Diagnostics

from ..groups import Contract
from ..operations import Operation
from ..workflows import Workflow, walk_workflow_steps
from .additional import validate_additional_contract
from .failures import validate_failures
from .index import SemanticIndex
from .presentations import validate_presentation_graphs
from .properties import validate_property_contract
from .schema_extensions import validate_schema_extensions
from .validator import ContractValidator as _BaseContractValidator, _error
from .value_sources import validate_value_sources


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

    def _validate_workflow(self, workflow: Workflow, index: SemanticIndex, diagnostics: list[Diagnostic]) -> None:
        for item in workflow.inputs:
            self._validate_schema_use(item, workflow, index, diagnostics)
        for item in workflow.outputs:
            self._validate_output(item, workflow, index, diagnostics)
        for failure in workflow.failures:
            self._require(failure, index.failures, "IR_MISSING_FAILURE", "workflow failure", workflow, diagnostics)
        self._validate_effects(workflow.effects, workflow, index, diagnostics)
        self._validate_workflow_facets(workflow.facets, workflow, index, diagnostics)
        steps = walk_workflow_steps(workflow.steps)
        step_names = {step.name for step in steps}
        for step in steps:
            self._validate_workflow_step(step, workflow, step_names, index, diagnostics)
        for transition in workflow.transitions:
            for label, step_name in (("source", transition.source), ("target", transition.target)):
                if step_name not in step_names:
                    diagnostics.append(_error("IR_MISSING_WORKFLOW_STEP", f"workflow transition {label} {step_name!r} does not exist", workflow, (("step", step_name),)))

    def validate(self, contract: Contract) -> Diagnostics:
        base = super().validate(contract)
        index, _ = SemanticIndex.build(contract)
        return base.extend(validate_property_contract(contract, index)).extend(validate_schema_extensions(contract, index)).extend(validate_failures(contract, index)).extend(validate_value_sources(contract, index)).extend(validate_presentation_graphs(contract)).extend(validate_additional_contract(contract, index))


def validate_contract(contract: Contract) -> Diagnostics:
    return ContractValidator().validate(contract)


__all__ = ["ContractValidator", "SemanticIndex", "validate_contract"]
