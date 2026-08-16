"""Validation, indexing and deterministic relationship resolution over Canonical IR."""

from dryv.ir import Contract, SemanticId
from dryv.ir.model.validation import SemanticIndex

from .indexing import IRSnapshot, build_object_index
from .resolution import dependency_graph, effective_schema, reverse_graph
from .validation import validate_ir


class IRFeature:
    def load(self, contract: Contract) -> IRSnapshot:
        diagnostics = validate_ir(contract)
        semantic_index, _ = SemanticIndex.build(contract)
        objects, kinds = build_object_index(contract, semantic_index)
        dependencies = dependency_graph(objects)
        return IRSnapshot(
            contract,
            diagnostics,
            semantic_index,
            objects,
            kinds,
            dependencies,
            reverse_graph(dependencies),
        )

    def effective_schema(self, snapshot: IRSnapshot, semantic_id: SemanticId):
        if semantic_id not in snapshot.semantic_index.schemas:
            raise KeyError(str(semantic_id))
        return effective_schema(semantic_id, snapshot.semantic_index.schemas)


__all__ = ["IRFeature", "IRSnapshot", "dependency_graph", "effective_schema", "reverse_graph", "validate_ir"]
