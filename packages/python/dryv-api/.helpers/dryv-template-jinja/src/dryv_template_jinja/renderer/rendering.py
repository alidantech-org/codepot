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
        environment = create_environment()
        template = environment.from_string(source)
        parts: list[str] = []
        for part in template.generate(**request.context.value):
            if cancelled():
                yield _failure(request.job_id, "JINJA_CANCELLED", "render cancelled")
                return
            parts.append(part)
        content = "".join(parts).encode("utf-8")
    except UnicodeDecodeError:
        yield _failure(request.job_id, "JINJA_TEMPLATE_UTF8", "Jinja templates must be UTF-8")
        return
    except (TemplateSyntaxError, UndefinedError, TemplateError, TypeError, ValueError) as exc:
        yield _failure(request.job_id, "JINJA_RENDER_FAILED", str(exc) or type(exc).__name__)
        return

    digest = hashlib.sha256(content).hexdigest()
    yield ArtifactBegin(
        request.job_id,
        request.output.artifact_id,
        request.output.path,
        "text/plain; charset=utf-8",
        len(content),
    )
    offset = 0
    while offset < len(content):
        if cancelled():
            yield _failure(request.job_id, "JINJA_CANCELLED", "render cancelled while streaming")
            return
        chunk = content[offset : offset + chunk_bytes]
        yield ArtifactChunk(request.job_id, request.output.artifact_id, offset, chunk)
        offset += len(chunk)
    yield ArtifactEnd(
        request.job_id,
        request.output.artifact_id,
        len(content),
        f"sha256:{digest}",
    )
    yield RenderComplete(request.job_id)


def _failure(job_id: str, code: str, message: str) -> RenderFailed:
    return RenderFailed(job_id, (RendererDiagnostic(code, message),))


__all__ = ["render_template"]
