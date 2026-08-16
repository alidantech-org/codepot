"""Resolve local input locations into explicit API uploads."""

from .author import ResolvedAuthor, resolve_author
from .destination import resolve_destination
from .ir import ResolvedIr, resolve_ir
from .packs import ResolvedPack, resolve_packs
from .resources import guess_media_type, resolve_project_resources, safe_local_file, upload_bytes, upload_file

__all__ = [
    "ResolvedAuthor",
    "ResolvedIr",
    "ResolvedPack",
    "guess_media_type",
    "resolve_author",
    "resolve_destination",
    "resolve_ir",
    "resolve_packs",
    "resolve_project_resources",
    "safe_local_file",
    "upload_bytes",
    "upload_file",
]
