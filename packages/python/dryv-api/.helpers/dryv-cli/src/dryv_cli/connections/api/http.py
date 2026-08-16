from __future__ import annotations

import base64
from dataclasses import dataclass
from typing import Any, BinaryIO

import httpx

from dryv_api import (
    BuildDiagnostic,
    BuildResourceUpload,
    BuildStatus,
    BuildSummary,
    CreateBuildRequest,
    PackBundleUpload,
)


class ApiHttpError(RuntimeError):
    def __init__(self, code: str, message: str, *, status_code: int | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


@dataclass(frozen=True, slots=True)
class BundleDownload:
    size: int
    content_hash: str
    artifact_count: int


class ApiHttpTransport:
    def __init__(self, base_url: str, *, timeout: float = 30.0) -> None:
        self.base_url = base_url.rstrip("/")
        self._client = httpx.Client(base_url=self.base_url, timeout=timeout, follow_redirects=False)

    def close(self) -> None:
        self._client.close()

    def create_build(self, request: CreateBuildRequest) -> BuildSummary:
        return _summary(self._json(self._client.post("/v1/builds", json=_build_document(request))))

    def get_build(self, build_id: str) -> BuildSummary:
        return _summary(self._json(self._client.get(f"/v1/builds/{build_id}")))

    def get_plan(self, build_id: str) -> dict[str, object]:
        return _object(self._json(self._client.get(f"/v1/builds/{build_id}/plan")))

    def preflight(self, build_id: str) -> BuildSummary:
        return _summary(self._json(self._client.post(f"/v1/builds/{build_id}/preflight")))

    def render(self, build_id: str) -> BuildSummary:
        return _summary(self._json(self._client.post(f"/v1/builds/{build_id}/render")))

    def cancel(self, build_id: str) -> BuildSummary:
        return _summary(self._json(self._client.post(f"/v1/builds/{build_id}/cancel")))

    def release(self, build_id: str) -> None:
        response = self._client.delete(f"/v1/builds/{build_id}")
        if response.status_code not in {204, 404}:
            self._raise(response)

    def download_bundle(self, build_id: str, target: BinaryIO) -> BundleDownload:
        with self._client.stream("GET", f"/v1/builds/{build_id}/bundle") as response:
            if response.status_code >= 400:
                self._raise(response)
            digest = response.headers.get("x-dryv-content-hash")
            count = response.headers.get("x-dryv-artifact-count")
            length = response.headers.get("content-length")
            if digest is None or count is None or length is None:
                raise ApiHttpError("CLI_API_BUNDLE_HEADERS", "bundle response is missing Dryv metadata")
            written = 0
            for chunk in response.iter_bytes():
                target.write(chunk)
                written += len(chunk)
            if written != int(length):
                raise ApiHttpError("CLI_API_BUNDLE_SIZE", "bundle transfer size does not match Content-Length")
            return BundleDownload(written, digest, int(count))

    def _json(self, response: httpx.Response) -> object:
        if response.status_code >= 400:
            self._raise(response)
        try:
            return response.json()
        except ValueError as exc:
            raise ApiHttpError("CLI_API_JSON", "dryv-api returned invalid JSON") from exc

    def _raise(self, response: httpx.Response) -> None:
        try:
            document = response.json()
        except ValueError:
            document = {}
        code = document.get("code") if isinstance(document, dict) else None
        message = document.get("message") if isinstance(document, dict) else None
        raise ApiHttpError(
            str(code or "CLI_API_HTTP"),
            str(message or f"dryv-api returned HTTP {response.status_code}"),
            status_code=response.status_code,
        )


def _build_document(request: CreateBuildRequest) -> dict[str, object]:
    return {
        "buildId": request.build_id,
        "delivery": request.delivery.value,
        "project": _resource_document(request.project),
        "canonicalIr": _resource_document(request.canonical_ir),
        "packs": [_pack_document(item) for item in request.packs],
        "resources": [_resource_document(item) for item in request.resources],
    }


def _pack_document(pack: PackBundleUpload) -> dict[str, object]:
    return {
        "instanceName": pack.instance_name,
        "manifest": _resource_document(pack.manifest),
        "resources": [
            {"relativePath": item.relative_path, "resource": _resource_document(item.resource)}
            for item in pack.resources
        ],
    }


def _resource_document(resource: BuildResourceUpload) -> dict[str, object]:
    return {
        "resourceId": resource.resource_id,
        "mediaType": resource.media_type,
        "contentHash": resource.content_hash,
        "contentBase64": base64.b64encode(resource.content).decode("ascii"),
    }


def _summary(value: object) -> BuildSummary:
    item = _object(value)
    diagnostics: list[BuildDiagnostic] = []
    raw_diagnostics = item.get("diagnostics", [])
    if not isinstance(raw_diagnostics, list):
        raise ApiHttpError("CLI_API_SUMMARY", "diagnostics must be an array")
    for raw in raw_diagnostics:
        diagnostic = _object(raw)
        details_raw = diagnostic.get("details", {})
        if not isinstance(details_raw, dict):
            raise ApiHttpError("CLI_API_SUMMARY", "diagnostic details must be an object")
        diagnostics.append(
            BuildDiagnostic(
                str(diagnostic.get("code", "API_UNKNOWN")),
                str(diagnostic.get("message", "")),
                str(diagnostic.get("level", "error")),
                diagnostic.get("subject") if isinstance(diagnostic.get("subject"), str) else None,
                tuple(sorted((str(key), str(value)) for key, value in details_raw.items())),
            )
        )
    try:
        status = BuildStatus(str(item["status"]))
    except (KeyError, ValueError) as exc:
        raise ApiHttpError("CLI_API_SUMMARY", "build summary has an invalid status") from exc
    return BuildSummary(
        str(item.get("buildId", "")),
        status,
        item.get("planHash") if isinstance(item.get("planHash"), str) else None,
        int(item.get("jobCount", 0)),
        int(item.get("artifactCount", 0)),
        tuple(diagnostics),
    )


def _object(value: object) -> dict[str, Any]:
    if not isinstance(value, dict) or not all(isinstance(key, str) for key in value):
        raise ApiHttpError("CLI_API_OBJECT", "dryv-api response must be a JSON object")
    return dict(value)


__all__ = ["ApiHttpError", "ApiHttpTransport", "BundleDownload"]
