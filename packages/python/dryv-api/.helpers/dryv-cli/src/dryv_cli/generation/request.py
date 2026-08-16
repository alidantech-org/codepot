from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4

from dryv_api import BuildResourceUpload, CreateBuildRequest, DeliveryMode

from dryv_cli.connections.author import AuthorClient, AuthorResult
from dryv_cli.project import LocalProject
from dryv_cli.resolvers import (
    resolve_author,
    resolve_ir,
    resolve_packs,
    resolve_project_resources,
    upload_bytes,
)


class GenerationRequestError(RuntimeError):
    def __init__(
        self,
        code: str,
        message: str,
        *,
        diagnostics: tuple[dict[str, object], ...] = (),
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.diagnostics = diagnostics


@dataclass(frozen=True, slots=True)
class CollectedBuild:
    request: CreateBuildRequest
    author_result: AuthorResult | None = None


def collect_build_request(
    project: LocalProject,
    *,
    author: AuthorClient,
    delivery: DeliveryMode = DeliveryMode.STREAM,
    build_id: str | None = None,
    ir_override: str | None = None,
    author_override: str | None = None,
) -> CollectedBuild:
    if ir_override is not None and author_override is not None:
        raise GenerationRequestError(
            "CLI_SOURCE_OVERRIDE",
            "provide at most one IR or Author source override",
        )

    ir = resolve_ir(project, ir_override) if author_override is None else None
    author_target = resolve_author(project, author_override) if ir_override is None else None
    author_result: AuthorResult | None = None

    if ir is not None:
        canonical_ir = ir.upload
    elif author_target is not None:
        author_result = author.compile(
            author_target.target,
            project_root=project.root,
            representation="json",
        )
        if not author_result.ok or author_result.content is None or author_result.media_type is None:
            raise GenerationRequestError(
                "CLI_AUTHOR_FAILED",
                "Author source did not compile into Canonical Dryv IR",
                diagnostics=author_result.diagnostics,
            )
        canonical_ir = upload_bytes(
            "resource://project/canonical-ir",
            author_result.media_type,
            author_result.content,
        )
    else:
        raise GenerationRequestError(
            "CLI_SOURCE_MISSING",
            "project must declare source.ir or source.author, or provide an explicit source override",
        )

    project_upload = upload_bytes(
        "resource://project/config",
        project.config_media_type,
        project.config_bytes,
    )
    packs = tuple(item.upload for item in resolve_packs(project))
    resources = resolve_project_resources(project)
    request = CreateBuildRequest(
        build_id=build_id or f"cli-{uuid4().hex}",
        project=project_upload,
        canonical_ir=canonical_ir,
        packs=packs,
        resources=resources,
        delivery=delivery,
    )
    return CollectedBuild(request, author_result)


__all__ = ["CollectedBuild", "GenerationRequestError", "collect_build_request"]
