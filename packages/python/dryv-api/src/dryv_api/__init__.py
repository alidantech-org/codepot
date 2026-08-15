"""Outer transport host for Dryv Runtime.

Clients exchange the versioned wire payloads owned here; only this host package
constructs and invokes the in-process DryvRuntime.
"""

from .service import (
    API_VERSION,
    ApiContractError,
    DryvApiService,
    RegisteredAuthorSession,
    RegisteredRenderSession,
    SessionRegistry,
    encode_build_result,
)

__all__ = [
    "API_VERSION",
    "ApiContractError",
    "DryvApiService",
    "RegisteredAuthorSession",
    "RegisteredRenderSession",
    "SessionRegistry",
    "encode_build_result",
]
