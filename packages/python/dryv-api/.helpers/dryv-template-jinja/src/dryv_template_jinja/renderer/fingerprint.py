from __future__ import annotations

import hashlib

import jinja2

PACKAGE_VERSION = "0.2.0a1"
RENDERER_ID = "jinja"
RENDERER_CAPABILITY = "jinja/v1"


def renderer_fingerprint() -> str:
    payload = "\0".join(
        (
            "dryv-template-jinja",
            PACKAGE_VERSION,
            f"jinja2:{jinja2.__version__}",
            "SandboxedEnvironment",
            "StrictUndefined",
            "autoescape:false",
            "async:false",
            "globals:empty",
            "trailing-newline:true",
        )
    )
    return f"sha256:{hashlib.sha256(payload.encode('utf-8')).hexdigest()}"


__all__ = ["PACKAGE_VERSION", "RENDERER_CAPABILITY", "RENDERER_ID", "renderer_fingerprint"]
