from __future__ import annotations

from hashlib import sha256
from pathlib import Path

from codepotg.api import CancellationToken, OperationCancelled
from codepotg.diagnostics import Diagnostic, Diagnostics, DiagnosticSeverity
from codepotg.ir import (
    IrCodecError,
    contract_from_json,
    contract_from_yaml,
    contract_to_json,
)
from codepotg.plugins import PluginCategory, PluginDescriptor, PluginTrust
from codepotg.ports import SourceAdapterRequest, SourceAdapterResult
from codepotg.versions import IR_API_VERSION, PLUGIN_API_VERSION, Version

_MAX_SOURCE_BYTES = 32 * 1024 * 1024

_PLUGIN = PluginDescriptor(
    id="ir",
    category=PluginCategory.SOURCE_ADAPTER,
    distribution="codepotg-core",
    version=Version.parse("2.0.0-alpha.1"),
    api_version=PLUGIN_API_VERSION,
    ir_version=IR_API_VERSION,
    aliases=("codepot-ir",),
    capabilities=(
        "format.json",
        "format.yaml",
        "source.file",
        "source.memory",
        "transport.canonical",
    ),
    trust=PluginTrust.EXECUTABLE,
    documentation="Canonical Codepot IR JSON/YAML transport source adapter.",
)


class IrDocumentSourceAdapter:
    @property
    def plugin(self) -> PluginDescriptor:
        return _PLUGIN

    def normalize(
        self,
        request: SourceAdapterRequest,
        cancellation: CancellationToken,
    ) -> SourceAdapterResult:
        try:
            cancellation.raise_if_cancelled()
            if request.options:
                raise IrCodecError(
                    "IR_SOURCE_OPTIONS",
                    "canonical IR sources do not accept adapter options",
                )
            content, suffix = _read(request)
            cancellation.raise_if_cancelled()
            if len(content) > _MAX_SOURCE_BYTES:
                raise IrCodecError(
                    "IR_SOURCE_LIMIT",
                    f"IR source exceeds {_MAX_SOURCE_BYTES} bytes",
                )
            contract = (
                contract_from_json(content)
                if suffix == ".json" or content.lstrip().startswith((b"{", b"["))
                else contract_from_yaml(content)
            )
            cancellation.raise_if_cancelled()
            canonical = contract_to_json(contract, pretty=False).encode("utf-8")
            digest = sha256(canonical).hexdigest()
            return SourceAdapterResult(
                contract=contract,
                digest=digest,
                diagnostics=Diagnostics(),
            )
        except OperationCancelled:
            return _failure("IR_SOURCE_CANCELLED", "IR source loading was cancelled")
        except (IrCodecError, OSError, UnicodeError, ValueError) as exc:
            code = getattr(exc, "code", "IR_SOURCE_FAILED")
            message = getattr(exc, "message", None) or str(exc) or "IR source failed"
            return _failure(code, message)


def create_plugin() -> IrDocumentSourceAdapter:
    return IrDocumentSourceAdapter()


def _read(request: SourceAdapterRequest) -> tuple[bytes, str]:
    if request.content is not None:
        return (
            request.content
            if isinstance(request.content, bytes)
            else request.content.encode("utf-8"),
            "",
        )
    assert request.location is not None
    path = Path(request.location)
    if not path.is_absolute():
        raise IrCodecError(
            "IR_SOURCE_PATH",
            "IR source locations must be absolute paths",
        )
    canonical = path.resolve(strict=True)
    if not canonical.is_file():
        raise IrCodecError("IR_SOURCE_PATH", "IR source must be a regular file")
    return canonical.read_bytes(), canonical.suffix.lower()


def _failure(code: str, message: str) -> SourceAdapterResult:
    diagnostic = Diagnostic(
        code=code,
        severity=DiagnosticSeverity.ERROR,
        message=message,
    )
    return SourceAdapterResult(
        contract=None,
        digest=None,
        diagnostics=Diagnostics((diagnostic,)),
    )
