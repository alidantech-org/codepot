from __future__ import annotations

from pathlib import Path

from dryv.features.serialization import contract_to_json, contract_to_jsonl, contract_to_yaml
from dryv.versions import IR_API_VERSION

from dryv_author.loading import discover_author

from .contracts import HostCompileRequest, HostCompileResponse


def compile_target(request: HostCompileRequest) -> HostCompileResponse:
    try:
        author = discover_author(request.target, project_root=Path(request.project_root).resolve() if request.project_root else None)
        result = author.compile()
        diagnostics = result.diagnostics.to_dict()
        if result.contract is None:
            return HostCompileResponse(False, None, None, diagnostics, str(IR_API_VERSION))
        if request.representation == "json":
            media_type = "application/vnd.dryv.ir+json"
            content = contract_to_json(result.contract, pretty=False)
        elif request.representation == "jsonl":
            media_type = "application/vnd.dryv.ir+jsonl"
            content = contract_to_jsonl(result.contract)
        else:
            media_type = "application/vnd.dryv.ir+yaml"
            content = contract_to_yaml(result.contract)
        return HostCompileResponse(True, media_type, content, diagnostics, str(IR_API_VERSION))
    except Exception as exc:
        return HostCompileResponse(False, None, None, ({"code": "AUTHOR_HOST_FAILED", "severity": "error", "message": str(exc) or type(exc).__name__, "span": None, "related": (), "details": {}, "suggestion": None, "documentation": None},), str(IR_API_VERSION))


__all__ = ["compile_target"]
