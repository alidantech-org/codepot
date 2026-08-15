from __future__ import annotations

import hashlib
import threading
from dataclasses import dataclass
from typing import Mapping

import jinja2
from jinja2 import StrictUndefined, TemplateError
from jinja2.sandbox import SandboxedEnvironment

PACKAGE_VERSION = "2.0.0a1"
RENDER_PROTOCOL_VERSION = 1
CONTEXT_VERSION = 1
RENDERER_CAPABILITY = "jinja/v1"
TEMPLATE_MEDIA_TYPES = (
    "text/x-jinja-template",
    "application/x-jinja-template",
)


@dataclass(frozen=True, slots=True)
class RendererHelloMessage:
    renderer_id: str
    renderer_version: str
    capabilities: tuple[str, ...]
    protocol_versions: tuple[int, ...]
    context_versions: tuple[int, ...]
    template_media_types: tuple[str, ...]
    fingerprint: str
    max_concurrency: int = 1
    deterministic: bool = True


@dataclass(frozen=True, slots=True)
class RenderDiagnosticMessage:
    code: str
    message: str
    severity: str = "error"


@dataclass(frozen=True, slots=True)
class RenderedOutputMessage:
    id: str
    content: bytes
    content_hash: str


@dataclass(frozen=True, slots=True)
class RenderResultMessage:
    job_id: str
    renderer_fingerprint: str
    outputs: tuple[RenderedOutputMessage, ...]
    diagnostics: tuple[RenderDiagnosticMessage, ...] = ()
    cancelled: bool = False


class JinjaRenderSession:
    """Protocol-shaped Jinja Render Client with no Dryv Engine dependency."""

    def __init__(self, *, max_concurrency: int = 1) -> None:
        if max_concurrency < 1:
            raise ValueError("max_concurrency must be positive")
        self._max_concurrency = max_concurrency
        self._cancelled: set[str] = set()
        self._lock = threading.Lock()
        self._environment = SandboxedEnvironment(
            autoescape=False,
            undefined=StrictUndefined,
            enable_async=False,
        )
        self._environment.globals.clear()

    def hello(self) -> RendererHelloMessage:
        fingerprint = _fingerprint()
        return RendererHelloMessage(
            renderer_id="jinja",
            renderer_version=PACKAGE_VERSION,
            capabilities=(RENDERER_CAPABILITY,),
            protocol_versions=(RENDER_PROTOCOL_VERSION,),
            context_versions=(CONTEXT_VERSION,),
            template_media_types=TEMPLATE_MEDIA_TYPES,
            fingerprint=fingerprint,
            max_concurrency=self._max_concurrency,
            deterministic=True,
        )

    def render(self, request: object) -> RenderResultMessage:
        job_id = _string_attr(request, "job_id")
        hello = self.hello()
        if self._is_cancelled(job_id):
            return RenderResultMessage(job_id, hello.fingerprint, (), cancelled=True)
        try:
            source = _bytes_attr(request, "template_content").decode("utf-8")
            context = _mapping_attr(request, "context")
            outputs = tuple(getattr(request, "outputs"))
            if len(outputs) != 1:
                return RenderResultMessage(
                    job_id,
                    hello.fingerprint,
                    (),
                    (
                        RenderDiagnosticMessage(
                            "JINJA_OUTPUT_CARDINALITY",
                            "Jinja Render Client requires one planned output per request",
                        ),
                    ),
                )
            template = self._environment.from_string(source)
            rendered_parts: list[str] = []
            for chunk in template.generate(**dict(context)):
                if self._is_cancelled(job_id):
                    return RenderResultMessage(job_id, hello.fingerprint, (), cancelled=True)
                rendered_parts.append(chunk)
            content = "".join(rendered_parts).encode("utf-8")
            output_id = _string_attr(outputs[0], "id")
            return RenderResultMessage(
                job_id,
                hello.fingerprint,
                (RenderedOutputMessage(output_id, content, _artifact_hash(content)),),
            )
        except (UnicodeDecodeError, TemplateError, TypeError, ValueError) as exc:
            return RenderResultMessage(
                job_id,
                hello.fingerprint,
                (),
                (
                    RenderDiagnosticMessage(
                        "JINJA_RENDER_FAILED",
                        str(exc) or type(exc).__name__,
                    ),
                ),
            )

    def cancel(self, job_id: str) -> None:
        with self._lock:
            self._cancelled.add(job_id)

    def _is_cancelled(self, job_id: str) -> bool:
        with self._lock:
            return job_id in self._cancelled


def _fingerprint() -> str:
    payload = f"dryv-template-jinja\0{PACKAGE_VERSION}\0jinja2\0{jinja2.__version__}\0strict-sandbox-v1"
    return f"sha256:{hashlib.sha256(payload.encode('utf-8')).hexdigest()}"


def _artifact_hash(content: bytes) -> str:
    digest = hashlib.sha256(content).hexdigest()
    return f"sha256:v1:artifact-content:{digest}"


def _string_attr(value: object, name: str) -> str:
    result = getattr(value, name, None)
    if not isinstance(result, str) or not result:
        raise ValueError(f"render request {name} must be a non-empty string")
    return result


def _bytes_attr(value: object, name: str) -> bytes:
    result = getattr(value, name, None)
    if not isinstance(result, bytes):
        raise ValueError(f"render request {name} must be bytes")
    return result


def _mapping_attr(value: object, name: str) -> Mapping[str, object]:
    result = getattr(value, name, None)
    if not isinstance(result, Mapping) or not all(isinstance(key, str) for key in result):
        raise ValueError(f"render request {name} must be a string-keyed mapping")
    return result


__all__ = [
    "CONTEXT_VERSION",
    "JinjaRenderSession",
    "PACKAGE_VERSION",
    "RENDERER_CAPABILITY",
    "RENDER_PROTOCOL_VERSION",
    "RenderDiagnosticMessage",
    "RenderResultMessage",
    "RenderedOutputMessage",
    "RendererHelloMessage",
    "TEMPLATE_MEDIA_TYPES",
]
