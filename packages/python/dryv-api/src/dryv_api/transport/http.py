from __future__ import annotations

import base64
from typing import Any

from starlette.concurrency import run_in_threadpool
from starlette.requests import Request
from starlette.responses import JSONResponse, Response, StreamingResponse

from dryv_api.contracts import (
    ApiContractError,
    BuildResourceUpload,
    BuildSummary,
    CreateBuildRequest,
    DeliveryMode,
    PackBundleUpload,
    PackResourceUpload,
)
from dryv_api.server import DryvApiServer


async def create_build(request: Request) -> Response:
    try:
        decoded = _decode_build(await request.json())
        session = await run_in_threadpool(_server(request).submit_build, decoded)
        return JSONResponse(_summary(session.summary()), status_code=201)
    except Exception as exc:
        return _error(exc)


async def get_build(request: Request) -> Response:
    try:
        session = await run_in_threadpool(
            _server(request).build,
            request.path_params["build_id"],
        )
        return JSONResponse(_summary(session.summary()))
    except Exception as exc:
        return _error(exc)


async def get_plan(request: Request) -> Response:
    try:
        session = await run_in_threadpool(
            _server(request).build,
            request.path_params["build_id"],
        )
        if session.plan is None:
            raise ApiContractError("API_PLAN_NOT_READY", "GenerationPlan is not ready")
        return JSONResponse(session.plan.canonical_document())
    except Exception as exc:
        return _error(exc)


async def preflight_build(request: Request) -> Response:
    try:
        server = _server(request)
        build_id = request.path_params["build_id"]
        await run_in_threadpool(server.preflight_build, build_id)
        session = await run_in_threadpool(server.build, build_id)
        return JSONResponse(_summary(session.summary()))
    except Exception as exc:
        return _error(exc)


async def render_build(request: Request) -> Response:
    try:
        server = _server(request)
        build_id = request.path_params["build_id"]
        await run_in_threadpool(server.render_build, build_id)
        session = await run_in_threadpool(server.build, build_id)
        return JSONResponse(_summary(session.summary()), status_code=202)
    except Exception as exc:
        return _error(exc)


async def cancel_build(request: Request) -> Response:
    try:
        server = _server(request)
        build_id = request.path_params["build_id"]
        await run_in_threadpool(server.cancel_build, build_id)
        session = await run_in_threadpool(server.build, build_id)
        return JSONResponse(_summary(session.summary()))
    except Exception as exc:
        return _error(exc)


async def delete_build(request: Request) -> Response:
    try:
        released = await run_in_threadpool(
            _server(request).release_build,
            request.path_params["build_id"],
        )
        return Response(status_code=204 if released else 404)
    except Exception as exc:
        return _error(exc)


async def get_bundle(request: Request) -> Response:
    try:
        handle = await run_in_threadpool(
            _server(request).bundle,
            request.path_params["build_id"],
        )
        if handle is None:
            raise ApiContractError("API_BUNDLE_MISSING", "build has no bundle delivery")
        if not handle.ready.is_set():
            return JSONResponse(
                {"code": "API_BUNDLE_NOT_READY", "message": "bundle is not ready"},
                status_code=409,
            )
        if handle.error is not None:
            raise ApiContractError("API_BUNDLE_FAILED", str(handle.error))
        metadata = handle.metadata
        assert metadata is not None
        return StreamingResponse(
            handle.chunks(),
            media_type="application/zip",
            headers={
                "content-length": str(metadata.size),
                "x-dryv-content-hash": metadata.content_hash,
                "x-dryv-artifact-count": str(metadata.artifact_count),
            },
        )
    except Exception as exc:
        return _error(exc)


def _server(request: Request) -> DryvApiServer:
    return request.app.state.dryv_server


def _decode_build(value: object) -> CreateBuildRequest:
    root = _object(value)
    _unknown(
        root,
        {"buildId", "delivery", "project", "canonicalIr", "packs", "resources"},
        "build",
    )
    return CreateBuildRequest(
        build_id=_string(root.get("buildId"), "buildId"),
        project=_decode_resource(root.get("project")),
        canonical_ir=_decode_resource(root.get("canonicalIr")),
        packs=tuple(_decode_pack(item) for item in _list(root.get("packs", []))),
        resources=tuple(_decode_resource(item) for item in _list(root.get("resources", []))),
        delivery=DeliveryMode(str(root.get("delivery", DeliveryMode.STREAM.value))),
    )


def _decode_pack(value: object) -> PackBundleUpload:
    item = _object(value)
    _unknown(item, {"instanceName", "manifest", "resources"}, "pack")
    resources: list[PackResourceUpload] = []
    for raw in _list(item.get("resources", [])):
        resource_item = _object(raw)
        _unknown(resource_item, {"relativePath", "resource"}, "pack resource")
        resources.append(
            PackResourceUpload(
                _string(resource_item.get("relativePath"), "relativePath"),
                _decode_resource(resource_item.get("resource")),
            )
        )
    return PackBundleUpload(
        _string(item.get("instanceName"), "instanceName"),
        _decode_resource(item.get("manifest")),
        tuple(resources),
    )


def _decode_resource(value: object) -> BuildResourceUpload:
    item = _object(value)
    _unknown(item, {"resourceId", "mediaType", "contentHash", "contentBase64"}, "resource")
    try:
        content = base64.b64decode(
            _string(item.get("contentBase64"), "contentBase64"),
            validate=True,
        )
    except Exception as exc:
        raise ApiContractError("API_RESOURCE_BASE64", "resource contentBase64 is invalid") from exc
    claimed = item.get("contentHash")
    if claimed is not None and not isinstance(claimed, str):
        raise ApiContractError("API_RESOURCE_HASH", "contentHash must be a string")
    return BuildResourceUpload(
        _string(item.get("resourceId"), "resourceId"),
        _string(item.get("mediaType"), "mediaType"),
        content,
        claimed,
    )


def _summary(value: BuildSummary) -> dict[str, object]:
    return {
        "buildId": value.build_id,
        "status": value.status.value,
        "planHash": value.plan_hash,
        "jobCount": value.job_count,
        "artifactCount": value.artifact_count,
        "diagnostics": [
            {
                "code": item.code,
                "message": item.message,
                "level": item.level,
                "subject": item.subject,
                "details": dict(item.details),
            }
            for item in value.diagnostics
        ],
    }


def _error(exc: Exception) -> JSONResponse:
    code = str(getattr(exc, "code", "API_HTTP_FAILED"))
    message = str(getattr(exc, "message", str(exc) or type(exc).__name__))
    status = (
        404
        if code.endswith("_MISSING")
        else 409
        if "NOT_READY" in code or "STATE" in code or "ACTIVE" in code
        else 400
    )
    return JSONResponse({"code": code, "message": message}, status_code=status)


def _object(value: object) -> dict[str, Any]:
    if not isinstance(value, dict) or not all(isinstance(key, str) for key in value):
        raise ApiContractError("API_HTTP_OBJECT", "expected JSON object")
    return value


def _list(value: object) -> list[object]:
    if not isinstance(value, list):
        raise ApiContractError("API_HTTP_LIST", "expected JSON array")
    return value


def _string(value: object, name: str) -> str:
    if not isinstance(value, str) or not value or value.strip() != value:
        raise ApiContractError("API_HTTP_STRING", f"{name} must be a non-empty trimmed string")
    return value


def _unknown(value: dict[str, object], allowed: set[str], label: str) -> None:
    unknown = sorted(set(value) - allowed)
    if unknown:
        raise ApiContractError(
            "API_HTTP_UNKNOWN_FIELD",
            f"{label} contains unknown field {unknown[0]!r}",
        )


__all__ = [
    "cancel_build",
    "create_build",
    "delete_build",
    "get_build",
    "get_bundle",
    "get_plan",
    "preflight_build",
    "render_build",
]
