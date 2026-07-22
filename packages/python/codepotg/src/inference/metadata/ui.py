"""Read compiler-resolved x-codegen UI metadata."""

from __future__ import annotations

from typing import Any

from constants.codegen import (
    ENABLED,
    INFERENCE_REASON,
    INFERENCE_SOURCE,
    INFERRED,
    ROLE,
    UI,
    X_CODEGEN,
)


def get_operation_ui_metadata(node: dict[str, Any] | None) -> dict[str, Any]:
    """Return normalized operation UI metadata from x-codegen.ui.

    The OpenAPI compiler owns UI role inference. This reader only reflects the
    final metadata emitted under x-codegen.ui.
    """
    if not isinstance(node, dict):
        return _disabled()

    x_codegen = node.get(X_CODEGEN)
    if not isinstance(x_codegen, dict):
        return _disabled()

    ui = x_codegen.get(UI)
    if not isinstance(ui, dict):
        return _disabled()

    enabled = ui.get(ENABLED) is True
    role = ui.get(ROLE) if isinstance(ui.get(ROLE), str) else None
    inferred = ui.get(INFERRED) is True
    inference_source = (
        ui.get(INFERENCE_SOURCE) if isinstance(ui.get(INFERENCE_SOURCE), str) else None
    )
    inference_reason = (
        ui.get(INFERENCE_REASON) if isinstance(ui.get(INFERENCE_REASON), str) else None
    )

    return {
        ENABLED: enabled,
        ROLE: role,
        INFERRED: inferred,
        INFERENCE_SOURCE: inference_source,
        INFERENCE_REASON: inference_reason,
    }


def _disabled() -> dict[str, Any]:
    return {
        ENABLED: False,
        ROLE: None,
        INFERRED: False,
        INFERENCE_SOURCE: None,
        INFERENCE_REASON: None,
    }
