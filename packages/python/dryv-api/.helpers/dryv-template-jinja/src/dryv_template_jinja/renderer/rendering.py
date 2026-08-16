from __future__ import annotations

import hashlib
from collections.abc import Callable, Iterable

from jinja2 import TemplateError, TemplateSyntaxError, UndefinedError

from dryv_api.renderers import (
    ArtifactBegin,
    ArtifactChunk,
    ArtifactEnd,
    RenderComplete,
    RenderFailed,
    RendererDiagnostic,
    RenderRequest,
)
from dryv_api.renderers.protocol import RenderStreamMessage

from .environment import create_environment
from .fingerprint import RENDERER_CAPABILITY


def render_template(
    request: RenderRequest,
    *,
    cancelled: Callable[[], bool],
    chunk_bytes: int = 64 * 1024,
) -> Iterable[RenderStreamMessage]:
    if chunk_bytes < 1:
        raise ValueError("chunk_bytes must be positive")
    if request.capability != RENDERER_CAPABILITY:
        yield _failure(request.job_id, "JINJA_CAPABILITY", f"unsupported renderer capability {request.capability!r}")
        return
    if cancelled():
        yield _failure(request.job_id, "JINJA_CANCELLED", "render cancelled before execution")
        return
    try:
        source = request.template.content.decode("utf-8")
        template = create_environment().from_string(source)
    except UnicodeDecodeError:
        yield _failure(request.job_id, "JINJA_TEMPLATE_UTF8", "Jinja templates must be UTF-8")
        return
    except (TemplateSyntaxError, TemplateError, TypeError, ValueError) as exc:
        yield _failure(request.job_id, "JINJA_RENDER_FAILED", str(exc) or type(exc).__name__)
        return

    yield ArtifactBegin(
        request.job_id,
        request.output.artifact_id,
        request.output.path,
        "text/plain; charset=utf-8",
        None,
    )
    digest = hashlib.sha256()
    pending = bytearray()
    offset = 0
    try:
        for part in template.generate(**request.context.value):
            if cancelled():
                yield _failure(request.job_id, "JINJA_CANCELLED", "render cancelled")
                return
            encoded = part.encode("utf-8")
            digest.update(encoded)
            pending.extend(encoded)
            while len(pending) >= chunk_bytes:
                chunk = bytes(pending[:chunk_bytes])
                del pending[:chunk_bytes]
                yield ArtifactChunk(request.job_id, request.output.artifact_id, offset, chunk)
                offset += len(chunk)
        if pending:
            chunk = bytes(pending)
            yield ArtifactChunk(request.job_id, request.output.artifact_id, offset, chunk)
            offset += len(chunk)
    except (UnicodeEncodeError, UndefinedError, TemplateError, TypeError, ValueError) as exc:
        yield _failure(request.job_id, "JINJA_RENDER_FAILED", str(exc) or type(exc).__name__)
        return

    yield ArtifactEnd(
        request.job_id,
        request.output.artifact_id,
        offset,
        f"sha256:{digest.hexdigest()}",
    )
    yield RenderComplete(request.job_id)


def _failure(job_id: str, code: str, message: str) -> RenderFailed:
    return RenderFailed(job_id, (RendererDiagnostic(code, message),))


__all__ = ["render_template"]
